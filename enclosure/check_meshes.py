"""Check ASCII STL exports using only the Python standard library."""
from collections import Counter, defaultdict
from pathlib import Path
import json


def inspect(path):
    vertices = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'vertex':
            vertices.append(tuple(float(x) for x in fields[1:4]))
    if not vertices or len(vertices) % 3:
        raise ValueError(f'{path}: expected ASCII STL triangles')
    faces = [vertices[i:i + 3] for i in range(0, len(vertices), 3)]
    edges = defaultdict(list)
    oriented = Counter()
    for i, face in enumerate(faces):
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))].append(i)
            oriented[(a, b)] += 1
    neighbors = defaultdict(set)
    for ids in edges.values():
        for i in ids:
            neighbors[i].update(ids)
    todo = set(range(len(faces)))
    components = []
    while todo:
        pending = [todo.pop()]
        ids = []
        while pending:
            i = pending.pop()
            ids.append(i)
            for j in neighbors[i] & todo:
                todo.remove(j)
                pending.append(j)
        points = [v for i in ids for v in faces[i]]
        components.append({
            'triangles': len(ids),
            'min': [min(v[k] for v in points) for k in range(3)],
            'max': [max(v[k] for v in points) for k in range(3)],
        })
    bad_edges = sum(len(ids) != 2 for ids in edges.values())
    bad_winding = sum(oriented[(a, b)] != oriented[(b, a)] for a, b in edges)
    volume = 0
    degenerate = 0
    for a, b, c in faces:
        cross = (b[1]*c[2]-b[2]*c[1], b[2]*c[0]-b[0]*c[2], b[0]*c[1]-b[1]*c[0])
        volume += sum(a[k]*cross[k] for k in range(3))/6
        u, v = [b[k]-a[k] for k in range(3)], [c[k]-a[k] for k in range(3)]
        area = (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        degenerate += sum(x*x for x in area) < 1e-16
    return {'file': path.name, 'triangles': len(faces), 'components': components,
            'nonmanifold_edges': bad_edges, 'winding_errors': bad_winding,
            'degenerate_triangles': degenerate, 'signed_volume_mm3': round(volume, 3),
            'passed': len(components) == 1 and bad_edges == 0 and bad_winding == 0
                      and degenerate == 0 and volume > 0}


if __name__ == '__main__':
    folder = Path(__file__).parent / 'validation'
    reports = [inspect(p) for p in sorted(folder.glob('*.stl'))]
    (folder / 'mesh_report.json').write_text(json.dumps(reports, indent=2) + '\n')
    print(json.dumps(reports, indent=2))
    raise SystemExit(0 if len(reports) == 9 and all(r['passed'] for r in reports) else 1)
