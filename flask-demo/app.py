from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home_page():
    return "Hello Flask!"

# GET /two_sum/<x>/<y>
@app.route("/two_sum/<int:x>/<int:y>")
def two_sum(x, y) -> str:
    return str(x + y)

# GET /get_param?name=Allen&age=22
@app.route("/get_param")
def get_param() -> str:
    name = request.args.get("name")
    age = request.args.get("age")
    if not name:
        return "What is your name?"
    if not age:
        return f"Hello {name}."
    return f"Hello {name}, you are {age} years old!"

"""
GET /api/v1/get_emp_info?emp_id=xxxxx

Example usage::
>>> import requests
>>> API_HOST = "http://127.0.0.1:50000"
>>> API_ENDPOINT_GET_EMP = "/api/v1/get_emp_info"
>>> requests.get(
        f"{API_HOST}{API_ENDPOINT_GET_EMP}",
        params={"emp_id": "E001"},
    ).json()
"""
@app.route("/api/v1/get_emp_info")
def get_emp_info() -> str:
    emp_id = request.args.get("emp_id")
    return {
        "emp_id": emp_id,
        "name": "Allen",
        "age": 22,
        "department": "IT"
    }

# POST /get_form_data
# body: {"name": "Allen", "age": 22}
@app.route("/get_form_data", methods=["GET", "POST"])
def get_form_data() -> str:
    html = """
    <form method="POST" action="/get_form_data">
        Name: <input type="text" name="name"><br>
        <input type="submit" value="Submit">
    </form>
    """
    name = request.form.get("name")
    if name:
        html += f"<h1>Hello {name}!</h1>"
    return html

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=50000)
