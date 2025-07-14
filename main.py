from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import render_template

@app.route('/view_qr/<filename>')
def view_qr(filename):
    qr_url = f"/static/uploads/{filename}"
    return render_template('view_qr.html', qr_url=qr_url)

