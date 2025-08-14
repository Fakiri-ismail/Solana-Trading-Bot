import os
import ast


def get_tree_structure(root_dir):
    """Return a 'tree'-style folder structure."""
    tree_str = ""
    for root, dirs, files in os.walk(root_dir):
        # Ignore unwanted folders
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "venv", ".git")]
        level = root.replace(root_dir, "").count(os.sep)
        indent = " " * 4 * level
        tree_str += f"{indent}📂 {os.path.basename(root)}/\n"
        subindent = " " * 4 * (level + 1)
        for f in files:
            if f.endswith(".py"):
                tree_str += f"{subindent}🐍 {f}\n"
            elif f.endswith(".json"):
                tree_str += f"{subindent}📜 {f}\n"
            elif f.endswith(".sh"):
                tree_str += f"{subindent}📄 {f}\n"
            elif f.endswith(".md"):
                tree_str += f"{subindent}📝 {f}\n"
    return tree_str


def parse_file(filepath):
    """Parse a Python file and return its classes and functions."""
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    return classes, functions


def generate_markdown(root_dir, output_file="docs/project_structure.md"):
    """Generate a Markdown roadmap file."""
    with open(output_file, "w", encoding="utf-8") as md:
        md.write("# 📌 Solana Trading Bot Roadmap\n\n")
        md.write("## 📂 Project Structure\n")
        md.write("```\n")
        md.write(get_tree_structure(root_dir))
        md.write("```\n\n")

        for root, dirs, filenames in os.walk(root_dir):
            # Ignore unwanted folders
            dirs[:] = [d for d in dirs if d not in ("__pycache__", "venv")]
            # Only keep Python files
            filenames = [f for f in filenames if f.endswith(".py")]
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, root_dir)

                classes, functions = parse_file(filepath)

                md.write(f"### `{rel_path}`\n")
                if classes:
                    md.write("#### Classes:\n")
                    for cls in classes:
                        md.write(f"- `{cls}`\n")
                if functions:
                    md.write("\n#### Functions:\n")
                    for func in functions:
                        md.write(f"- `{func}`\n")
                md.write("\n")


if __name__ == "__main__":
    abs_path =os.path.abspath(__file__)
    project_path = abs_path.split("Solana-Trading-Bot")[0] + "Solana-Trading-Bot"
    generate_markdown(project_path)
    print("✅ Roadmap generated in project_structure.md")
