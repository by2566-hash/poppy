# Harness-side figure introspection: every matplotlib savefig also writes <file>.figure.json (prototype).
import json, os
try:
    import matplotlib.figure as _mf
    _orig = _mf.Figure.savefig
    def _dump(fig, fname):
        axes_out = []
        for ax in fig.get_axes():
            texts = [t for t in ax.texts] + [ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()
            r = fig.canvas.get_renderer()
            boxes = [(t.get_text(), t.get_window_extent(r)) for t in texts if t.get_text()]
            overlaps = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i+1:] if a[1].overlaps(b[1])]
            axes_out.append({
                "title": ax.get_title(), "xlabel": ax.get_xlabel(), "ylabel": ax.get_ylabel(),
                "xlim": list(ax.get_xlim()), "ylim": list(ax.get_ylim()), "yscale": ax.get_yscale(),
                "xticklabels": [t.get_text() for t in ax.get_xticklabels()],
                "legend": [t.get_text() for t in ax.get_legend().get_texts()] if ax.get_legend() else [],
                "bars": [{"x": float(p.get_x() + p.get_width()/2), "height": float(p.get_height())} for p in ax.patches if hasattr(p, "get_height")],
                "lines": [{"label": l.get_label(), "n": len(l.get_xdata()), "y": [float(v) for v in l.get_ydata()][:200]} for l in ax.get_lines()],
                "text_overlaps": overlaps[:20], "n_texts": len(boxes)})
        with open(str(fname) + ".figure.json", "w") as f:
            json.dump({"axes": axes_out, "size_in": [float(v) for v in fig.get_size_inches()]}, f, default=float)
    def savefig(self, fname, *a, **k):
        out = _orig(self, fname, *a, **k)
        try:
            if isinstance(fname, (str, os.PathLike)): _dump(self, fname)
        except Exception as e:  # never break the agent's run
            open(str(fname) + ".figure.err", "w").write(repr(e))
        return out
    _mf.Figure.savefig = savefig
except Exception:
    pass
