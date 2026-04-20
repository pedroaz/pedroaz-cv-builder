import json
import webbrowser
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, redirect

from .generator import CVGenerator
from .schema import CVSchema

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
app.config["DATA_DIR"] = Path("data")
app.config["OUTPUT_DIR"] = Path("output")

schema = CVSchema()


@app.route("/")
def index():
    return redirect("/editor/resume")


@app.route("/editor/<name>")
def editor(name):
    data_dir = app.config["DATA_DIR"]
    cv_path = data_dir / f"{name}.json"

    if cv_path.exists():
        with open(cv_path) as f:
            cv_data = json.load(f)
    else:
        cv_data = {"basics": {"name": "", "email": ""}}

    return render_template("editor.html", cv_name=name, cv_data=json.dumps(cv_data, indent=2))


@app.route("/api/save", methods=["POST"])
def save():
    from weasyprint import HTML, CSS

    data = request.json
    name = data.get("name", "resume")
    cv_data = data.get("data")

    data_dir = app.config["DATA_DIR"]
    data_dir.mkdir(parents=True, exist_ok=True)

    cv_path = data_dir / f"{name}.json"
    with open(cv_path, "w") as f:
        json.dump(cv_data, f, indent=2)

    valid, errors = schema.validate(cv_data)

    output_dir = app.config["OUTPUT_DIR"]
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "preview.pdf"

    generator = CVGenerator()
    html_content = generator.generate(cv_data)

    template_dir = Path(__file__).parent / "templates"
    css_path = template_dir / "styles.css"
    with open(css_path) as f:
        css_content = f.read()

    HTML(string=html_content).write_pdf(
        pdf_path,
        stylesheets=[CSS(string=css_content)]
    )

    return jsonify({"success": True, "valid": valid, "errors": errors})


@app.route("/api/preview", methods=["GET", "POST"])
def preview():
    from weasyprint import HTML, CSS

    output_dir = app.config["OUTPUT_DIR"]
    pdf_path = output_dir / "preview.pdf"

    if request.method == "POST":
        data = request.json
        cv_data = data.get("data")

        valid, errors = schema.validate(cv_data)
        if not valid:
            return jsonify({"success": False, "errors": errors}), 400

        generator = CVGenerator()
        html_content = generator.generate(cv_data)

        template_dir = Path(__file__).parent / "templates"
        css_path = template_dir / "styles.css"
        with open(css_path) as f:
            css_content = f.read()

        output_dir.mkdir(parents=True, exist_ok=True)
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=css_content)]
        )
    else:
        if not pdf_path.exists():
            return "No preview available", 404

    return send_file(pdf_path, mimetype="application/pdf")


@app.route("/api/export/<name>")
def export(name):
    from weasyprint import HTML, CSS

    data_dir = app.config["DATA_DIR"]
    cv_path = data_dir / f"{name}.json"

    if not cv_path.exists():
        return jsonify({"error": "CV not found"}), 404

    with open(cv_path) as f:
        cv_data = json.load(f)

    generator = CVGenerator()
    html_content = generator.generate(cv_data)

    template_dir = Path(__file__).parent / "templates"
    css_path = template_dir / "styles.css"
    with open(css_path) as f:
        css_content = f.read()

    output_dir = app.config["OUTPUT_DIR"]
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{name}.pdf"

    HTML(string=html_content).write_pdf(
        pdf_path,
        stylesheets=[CSS(string=css_content)]
    )

    return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name=f"{name}.pdf")


def run_server(host="127.0.0.1", port=5000, data_dir="data"):
    app.config["DATA_DIR"] = Path(data_dir).resolve()
    app.config["OUTPUT_DIR"] = Path(data_dir).resolve().parent / "output"

    template_dir = Path(__file__).parent / "templates"
    if not (template_dir / "editor.html").exists():
        create_web_templates(template_dir)

    url = f"http://{host}:{port}"
    print(f"Opening {url}")
    webbrowser.open(url)
    app.run(host=host, port=port, debug=True)


def create_web_templates(template_dir):
    editor_html = template_dir / "editor.html"
    editor_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit: {{ cv_name }}</title>
    <style>
        body { font-family: system-ui, sans-serif; margin: 0; background: #f5f5f5; }
        .container { display: flex; height: 100vh; }
        .editor-pane { width: 50%; padding: 1em; overflow: auto; }
        .preview-pane { width: 50%; background: #ddd; padding: 1em; overflow: auto; }
        textarea { width: 100%; height: calc(100vh - 120px); font-family: Monaco, monospace; font-size: 12px; border: none; padding: 1em; resize: none; }
        iframe { width: 100%; height: calc(100vh - 120px); border: none; background: white; }
        .header { background: #2c3e50; color: white; padding: 1em; display: flex; justify-content: space-between; align-items: center; }
        .header a { color: white; margin-left: 1em; }
        .btn { background: #3498db; color: white; border: none; padding: 0.5em 1em; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
    </style>
</head>
<body>
    <div class="header">
        <span>Editing: {{ cv_name }}</span>
        <div>
            <button class="btn btn-success" onclick="save()">Save</button>
            <a href="/api/export/{{ cv_name }}" class="btn" style="background:#27ae60;">Download PDF</a>
        </div>
    </div>
    <div class="container">
        <div class="editor-pane">
            <textarea id="jsonEditor">{{ cv_data }}</textarea>
        </div>
        <div class="preview-pane">
            <iframe id="previewFrame" title="Preview"></iframe>
        </div>
    </div>

    <script>
        const cvName = "{{ cv_name }}";
        const previewFrame = document.getElementById('previewFrame');

        async function save() {
            const data = getEditorValue();
            if (!data) return;

            await fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: cvName, data: data})
            });

            previewFrame.src = previewFrame.src;
        }

        function getEditorValue() {
            const editor = document.getElementById('jsonEditor');
            try {
                return JSON.parse(editor.value);
            } catch (e) {
                return null;
            }
        }
    </script>
</body>
</html>""")


if __name__ == "__main__":
    app.run(debug=True)