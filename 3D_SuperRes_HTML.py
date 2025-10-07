#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL → interactive HTML (Plotly) with CUDA/CuPy-accelerated mesh decimation.
- Shows detected GPU info before any GPU work
- Uses CuPy when available; otherwise falls back to NumPy CPU decimation

Requirements (in your conda env):
  pip install plotly tqdm
  pip install cupy-cuda12x   # or the CuPy wheel matching your CUDA/toolkit; you already have CuPy working.

Notes:
- File I/O (STL read), Plotly, and Tk run on CPU (that’s normal).
- The heavy array ops for decimation run on GPU when possible.
"""

import os
import struct
import webbrowser
import numpy as np
from tkinter import Tk, filedialog, messagebox, simpledialog
from tqdm import tqdm
import plotly.graph_objects as go

# ---------------- GPU detection / info ----------------
_GPU_OK = False
_GPU_ERR = None
_GPU_SUMMARY = "GPU: (not detected)"
try:
    import cupy as cp
    try:
        ndev = cp.cuda.runtime.getDeviceCount()
        if ndev > 0:
            props = cp.cuda.runtime.getDeviceProperties(0)
            name = props['name'].decode() if isinstance(props['name'], bytes) else props['name']
            mem_gb = props['totalGlobalMem'] / (1024**3)
            cc = f"{props['major']}.{props['minor']}"
            # Driver/toolkit versions (may be unavailable on some stacks)
            try:
                drv_v = cp.cuda.runtime.driverGetVersion()
                rt_v  = cp.cuda.runtime.runtimeGetVersion()
                def vstr(v):  # e.g. 12010 -> '12.1'
                    major, minor = v // 1000, (v % 1000) // 10
                    return f"{major}.{minor}"
                info = f"CUDA driver {vstr(drv_v)}, toolkit {vstr(rt_v)}"
            except Exception:
                info = "CUDA version info unavailable"
            _GPU_OK = True
            _GPU_SUMMARY = f"{name} | {mem_gb:.1f} GB | CC {cc} | {info}"
        else:
            _GPU_SUMMARY = "No CUDA devices reported by CuPy."
    except Exception as e:
        _GPU_ERR = e
        _GPU_SUMMARY = f"CuPy found but device query failed: {e}"
except Exception as e:
    _GPU_ERR = e
    _GPU_SUMMARY = f"CuPy import failed: {e}"


# ---------------- UI helpers ----------------
def select_stl_file():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select STL file",
        filetypes=[("STL files", "*.stl")]
    )


def show_gpu_summary_dialog():
    root = Tk(); root.withdraw()
    msg = f"Detected environment:\n{_GPU_SUMMARY}"
    messagebox.showinfo("GPU Preflight", msg)


# ---------------- STL loading (CPU) ----------------
def load_stl(file_path):
    """Load a binary STL file quickly using a single NumPy read."""
    with open(file_path, 'rb') as f:
        _ = f.read(80)  # header
        num_triangles_bytes = f.read(4)
        if len(num_triangles_bytes) != 4:
            raise ValueError("Invalid STL: missing triangle count.")
        num_triangles = struct.unpack('<I', num_triangles_bytes)[0]

    expected_size = 84 + num_triangles * 50
    file_size = os.path.getsize(file_path)
    if expected_size > file_size + 100:
        raise ValueError("File doesn't appear to be standard binary STL (size mismatch).")

    tri_dtype = np.dtype([
        ('normal', '<f4', (3,)),
        ('v1',     '<f4', (3,)),
        ('v2',     '<f4', (3,)),
        ('v3',     '<f4', (3,)),
        ('attr',   '<u2')
    ])

    triangles = np.fromfile(file_path, dtype=tri_dtype, count=num_triangles, offset=84)

    vertices = np.empty((num_triangles * 3, 3), dtype=np.float32)
    vertices[0::3] = triangles['v1']
    vertices[1::3] = triangles['v2']
    vertices[2::3] = triangles['v3']

    faces = np.arange(num_triangles * 3, dtype=np.int32).reshape((-1, 3))
    return vertices, faces


# ---------------- CPU decimator (fallback) ----------------
def decimate_mesh_cpu(vertices, faces, target_percentage=0.30, seed=42):
    """CPU fallback: random face keep + unique-vertex compaction (NumPy)."""
    if not (0.05 <= target_percentage <= 1.0):
        raise ValueError("target_percentage must be between 0.05 and 1.0")
    print(f"🟡 CPU decimation: keeping {int(target_percentage * 100)}% of faces...")

    total_faces = faces.shape[0]
    keep_faces = int(total_faces * target_percentage)
    if keep_faces < 3:
        raise ValueError("Too few faces after decimation!")

    rng = np.random.default_rng(seed)
    sel = rng.permutation(total_faces)[:keep_faces]
    f_sel = faces[sel]

    used_idx = f_sel.reshape(-1)
    verts_used = vertices[used_idx]

    # Unique rows (NumPy) + inverse mapping
    unique_vertices, inverse = np.unique(verts_used, axis=0, return_inverse=True)
    faces_compact = inverse.reshape(-1, 3).astype(np.int32)

    print(f"✅ CPU decimated to {faces_compact.shape[0]} faces and {unique_vertices.shape[0]} vertices.")
    return unique_vertices, faces_compact


# ---------------- GPU decimator (CuPy) ----------------
def decimate_mesh_gpu(vertices_np, faces_np, target_percentage=0.30, seed=42):
    """
    CuPy decimator: random face keep + unique-vertex compaction via lexsort.
    Returns CPU arrays (vertices, faces) for Plotly.
    """
    if not _GPU_OK:
        raise RuntimeError(
            "CuPy/CUDA not ready for GPU decimation.\n"
            f"Detail: {_GPU_SUMMARY}"
        )
    if not (0.05 <= target_percentage <= 1.0):
        raise ValueError("target_percentage must be between 0.05 and 1.0")

    print(f"🔵 GPU decimation: keeping {int(target_percentage * 100)}% of faces...")

    v = cp.asarray(vertices_np, dtype=cp.float32)   # (N,3)
    f = cp.asarray(faces_np, dtype=cp.int32)        # (M,3)

    total_faces = f.shape[0]
    keep_faces = int(total_faces * target_percentage)
    if keep_faces < 3:
        raise ValueError("Too few faces after decimation!")

    cp.random.seed(seed)
    sel = cp.random.permutation(total_faces)[:keep_faces]
    f_sel = f[sel]                                  # (keep_faces,3)

    used_idx = f_sel.reshape(-1)                    # (keep_faces*3,)
    verts_used = v[used_idx]                        # (keep_faces*3, 3)
    verts_used = cp.ascontiguousarray(verts_used)

    # CuPy's lexsort expects a stacked (keys, N) array. Sort by z, y, x (last key is primary).
    keys = cp.stack((verts_used[:, 2], verts_used[:, 1], verts_used[:, 0]), axis=0)
    order = cp.lexsort(keys)
    vu_sorted = verts_used[order]
    n = vu_sorted.shape[0]

    if n == 0:
        unique_vertices = vu_sorted
        inverse = cp.empty((0,), dtype=cp.int64)
    else:
        change = cp.empty(n, dtype=cp.bool_)
        change[0] = True
        change[1:] = cp.any(vu_sorted[1:] != vu_sorted[:-1], axis=1)

        unique_vertices = vu_sorted[change]         # (K,3)
        group_ids_sorted = cp.cumsum(change) - 1    # 0..K-1
        inverse = cp.empty(n, dtype=cp.int64)
        inverse[order] = group_ids_sorted

    faces_compact = inverse.reshape(-1, 3).astype(cp.int32)

    unique_vertices_np = cp.asnumpy(unique_vertices)
    faces_compact_np = cp.asnumpy(faces_compact)

    print(f"✅ GPU decimated to {faces_compact_np.shape[0]} faces and {unique_vertices_np.shape[0]} vertices.")
    return unique_vertices_np, faces_compact_np


# ---------------- HTML export (CPU) ----------------
def save_as_html(vertices, faces, output_html_path):
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i = faces[:, 0]
    j = faces[:, 1]
    k = faces[:, 2]

    fig = go.Figure(data=[
        go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, opacity=0.7, color='lightblue')
    ])
    fig.update_layout(
        title='Interactive 3D STL Model',
        scene=dict(
            xaxis_title='X (microns)',
            yaxis_title='Y (microns)',
            zaxis_title='Z (microns)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig.write_html(output_html_path)
    print(f"✅ HTML saved: {output_html_path}")
    try:
        webbrowser.open(f'file://{os.path.abspath(output_html_path)}')
    except Exception:
        pass
    root = Tk(); root.withdraw()
    messagebox.showinfo("Success!", f"Interactive 3D HTML saved:\n{output_html_path}")


# ---------------- Main flow ----------------
def stl_to_html():
    # Show GPU summary first (per your request)
    show_gpu_summary_dialog()

    stl_file = select_stl_file()
    if not stl_file:
        print("❗ No file selected. Exiting.")
        return

    print("📦 Loading STL…")
    vertices, faces = load_stl(stl_file)
    print(f"📐 Loaded mesh: {vertices.shape[0]} vertices (flattened), {faces.shape[0]} faces")

    root = Tk(); root.withdraw()
    do_decimate = messagebox.askyesno(
        "Decimation?",
        "Reduce mesh for faster display?\n(Uses GPU when available)"
    )

    if do_decimate:
        percent = simpledialog.askfloat(
            "Decimation Percentage",
            "Enter fraction of faces to keep (e.g., 0.30 = 30%):",
            minvalue=0.05, maxvalue=1.0
        )
        if percent is not None:
            if _GPU_OK:
                try:
                    vertices, faces = decimate_mesh_gpu(vertices, faces, target_percentage=percent)
                except Exception as e:
                    print(f"GPU decimation failed ({e}). Falling back to CPU.")
                    vertices, faces = decimate_mesh_cpu(vertices, faces, target_percentage=percent)
            else:
                print("GPU not available; using CPU decimation.")
                vertices, faces = decimate_mesh_cpu(vertices, faces, target_percentage=percent)

    output_dir = os.path.dirname(stl_file)
    base_name = os.path.splitext(os.path.basename(stl_file))[0]
    output_html = os.path.join(output_dir, f"{base_name}_interactive.html")
    save_as_html(vertices, faces, output_html)


if __name__ == "__main__":
    stl_to_html()
