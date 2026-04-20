import argparse
import json
import sys
from pathlib import Path

from .generator import CVGenerator
from .schema import CVSchema


def render_command(args):
    from weasyprint import HTML, CSS

    cv_path = Path(args.input)
    output_path = Path(args.output)

    with open(cv_path) as f:
        data = json.load(f)

    schema = CVSchema()
    valid, errors = schema.validate(data)
    if not valid:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        if args.strict:
            sys.exit(1)

    generator = CVGenerator(template_name=args.template)
    html_content = generator.generate(data)

    basics = data.get("basics", {})
    image = basics.get("image", "")
    if image:
        import shutil
        image_source = Path(__file__).parent.parent / image
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(image_source, output_dir / image)
        html_content = html_content.replace(f"file://{image_source.resolve()}", image)

    template_dir = Path(__file__).parent / "templates"
    css_path = template_dir / "styles.css"
    with open(css_path) as f:
        css_content = f.read()

    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_content)]
    )
    print(f"PDF generated: {output_path}")


def validate_command(args):
    schema = CVSchema()
    cv_path = Path(args.input)

    if cv_path.is_dir():
        json_files = list(cv_path.glob("*.json"))
        for jf in json_files:
            valid, errors = schema.validate_file(jf)
            status = "✓" if valid else "✗"
            print(f"{status} {jf.name}")
            if not valid:
                for e in errors[:5]:
                    print(f"    {e}")
    else:
        valid, errors = schema.validate_file(cv_path)
        if valid:
            print("✓ Valid")
        else:
            print("✗ Invalid:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)


def html_command(args):
    cv_path = Path(args.input)
    output_path = Path(args.output)

    with open(cv_path) as f:
        data = json.load(f)

    generator = CVGenerator(template_name=args.template)
    html_content = generator.generate(data)

    basics = data.get("basics", {})
    image = basics.get("image", "")
    if image:
        import shutil
        image_source = Path(__file__).parent.parent / image
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(image_source, output_dir / image)
        html_content = html_content.replace(f"file://{image_source.resolve()}", image)

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"HTML generated: {output_path}")


def serve_command(args):
    from .web import run_server
    run_server(host=args.host, port=args.port, data_dir=args.data_dir)


def main():
    parser = argparse.ArgumentParser(description="CV Builder - Generate PDF CVs from JSON")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    render_parser = subparsers.add_parser("render", help="Generate PDF from JSON")
    render_parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    render_parser.add_argument("-o", "--output", required=True, help="Output PDF file")
    render_parser.add_argument("-t", "--template", default="modern", help="Template name")
    render_parser.add_argument("--strict", action="store_true", help="Fail on validation errors")

    validate_parser = subparsers.add_parser("validate", help="Validate JSON against schema")
    validate_parser.add_argument("-i", "--input", required=True, help="Input JSON file or directory")

    html_parser = subparsers.add_parser("html", help="Generate HTML from JSON")
    html_parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    html_parser.add_argument("-o", "--output", required=True, help="Output HTML file")
    html_parser.add_argument("-t", "--template", default="modern", help="Template name")

    serve_parser = subparsers.add_parser("serve", help="Start web UI")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    serve_parser.add_argument("--data-dir", default="data", help="Data directory")

    args = parser.parse_args()

    if args.command == "render":
        render_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "html":
        html_command(args)
    elif args.command == "serve":
        serve_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
