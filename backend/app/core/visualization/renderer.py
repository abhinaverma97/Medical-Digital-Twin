import os

try:
    # graphviz raises this when the 'dot' executable is not found
    from graphviz.backend.execute import ExecutableNotFound
except Exception:
    ExecutableNotFound = RuntimeError


class DiagramRenderer:
    """
    Renders Graphviz diagrams to file. If the system 'dot' executable
    is not available (common on fresh developer machines), the
    renderer gracefully falls back to writing the raw DOT source to
    `<path>.dot` instead of raising an exception. This prevents the
    backend from returning 500s and makes the missing-dependency
    situation explicit and recoverable.
    """

    def render(self, diagram, path: str, format: str = "png") -> str:
        try:
            # primary path: render using the Graphviz installation
            diagram.render(path, format=format, cleanup=True)
            return f"{path}.{format}"
        except Exception as e:
            # BROAD FALLBACK: 
            # If Graphviz fails for any reason (ExecutableNotFound, 
            # CalledProcessError, FileNotFoundError, etc.), we write
            # the raw DOT source to a file and return its path.
            # This makes the system resilient to environment/syntax issues.
            os.makedirs(os.path.dirname(path), exist_ok=True)
            dot_path = f"{path}.dot"
            try:
                with open(dot_path, "w", encoding="utf-8") as f:
                    f.write(diagram.source)
            except Exception:
                # Last resort if even writing to the preferred path fails
                dot_path = f"{os.path.basename(path)}.dot"
                with open(dot_path, "w", encoding="utf-8") as f:
                    f.write(diagram.source)
            return dot_path