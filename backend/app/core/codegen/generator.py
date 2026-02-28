import os
from jinja2 import Environment, FileSystemLoader


class CodeGenerator:
    """
    Deterministic, model-driven code generator.
    """

    def __init__(self, template_dir: str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_repo(
        self,
        design_graph,
        requirements,
        output_dir: str
    ):
        os.makedirs(output_dir, exist_ok=True)

        self._generate_main(output_dir)

        # Handle design_graph as dict (new dynamic design system)
        if isinstance(design_graph, dict):
            subsystems_list = design_graph.get("subsystems", [])
            for subsystem in subsystems_list:
                if isinstance(subsystem, dict):
                    subsystem_name = subsystem.get("id", "unknown")
                    # Build a simple node-like object for template rendering
                    node = type("Node", (), {
                        "inputs": subsystem.get("interfaces", []),
                        "outputs": subsystem.get("interfaces", []),
                    })()
                    self._generate_subsystem_module(
                        subsystem_name, node, requirements, output_dir
                    )
        else:
            for subsystem_name, node in design_graph.subsystems.items():
                self._generate_subsystem_module(
                    subsystem_name, node, requirements, output_dir
                )

    def _generate_subsystem_module(
        self, name, node, requirements, output_dir
    ):
        template = self.env.get_template("module.py.j2")

        subsystem_reqs = [
            r for r in requirements if r.subsystem == name
        ]

        # Sanitize filename: 'Safety/Alarm System' -> 'safety_alarm_system.py'
        safe_filename = name.lower().replace("/", "_").replace(" ", "_")
        file_path = os.path.join(output_dir, f"{safe_filename}.py")

        content = template.render(
            subsystem=name,
            inputs=node.inputs,
            outputs=node.outputs,
            requirements=subsystem_reqs
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_main(self, output_dir):
        template = self.env.get_template("main.py.j2")
        content = template.render()
        file_path = os.path.join(output_dir, "main.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)