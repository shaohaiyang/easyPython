from robyn import Robyn, static_file, jsonify
from robyn.templating import JinjaTemplate
from urllib.parse import parse_qs
from prisma import Prisma
from os import path

DEBUG=True
db = Prisma(auto_register=True)
db.connect()

app = Robyn(__file__)

current_dir = path.dirname(__file__)
JINJA_TEMPLATE = JinjaTemplate(path.join(current_dir, "templates"))

@app.get("/")
@app.get("/post")
async def h(req):
	try:
		#posts = db.post.query_raw('''select * from Post order by title desc''')
		posts = db.post.find_many( order={"title":'asc'}, include={"author": True} )

		context = {
			"framework": "Robyn",
			"templating_engine": "Jinja2",
			"data": posts
		}
		if DEBUG: print(context)
	
		template = JINJA_TEMPLATE.render_template(template_name="index.html", **context)
		return {
			"status_code": 200,
			"body": template,
			"type": "html",
		}
	except Exception as e:
		raise(e)


@app.post("/submit")
async def addpost(req):
	data = parse_qs(bytearray(req["body"]).decode("utf-8"))
	title = data["title"][0]
	author = data["author"][0]

	if title is None or author is None:
		return jsonify({
			"error": "you need to provide title and author!"
		})
		
	user = db.user.find_first(where={'name': author})
	if user is None:
		user = db.user.create(
			data={
				"name": author,
			}
		)

	post = db.post.create(
		data={
			'title': title,
			'authorId': user.id,
		}
	)
	if DEBUG: print("post data: <", data, " >>> ", title, author, post.id)

	return {
		"status": "200",
		"body": f"""<tr>
		<td>{post.title}</td>
		<td>{post.views}</td>
		<td>{author}</td>
		<td>{post.updatedAt}</td>
		<td>
		<button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
		<button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
		</td>
		</tr>""",
		"headers": {"Content-Type": "text/html"},
	}


@app.get("/post/:id")
async def getpost(req):
	try:
		postId = int(req["params"]["id"])
		if DEBUG: print(postId, "view")

		post = db.post.find_unique(where={'id': postId}, include={'author': True})
		if DEBUG: print(post)

		if post is None:
			return jsonify({"error": "Post doesn't exist"})

		response = f"""<tr>
		<td>{post.title}</td>
		<td>{post.views}</td>
		<td>{post.author.name}</td>
		<td>{post.updatedAt}</td>
		<td>
		<button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
		<button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
		</td>
		</tr>"""
		return response
	except Exception as e:
		raise(e)


@app.put("/edit/:id")
async def edit(req):
	postId = int(req["params"]["id"])
	if DEBUG: print(postId," edit")

	post = db.post.find_unique(where={'id': postId}, include={'author': True})
	if DEBUG: print(post)

	response = f"""
		<tr hx-trigger='cancel' class='editing' hx-get='/post/{post.id}' hx-swap='outerHTML'>
		<td><input name='title' value='{post.title}'/></td>
		<td>{post.views}</td>
		<td>{post.author.name}</td>
		<td>{post.updatedAt}</td>
		<td>
			<button class='btn btn-info' hx-get='/post/{post.id}'> Cancel </button>
			<button class='btn btn-primary' hx-put='/update/{post.id}' hx-include='closest tr'> Save </button>
		</td>
    </tr>"""

	return {
		"status": 200,
		"body": response,
		"headers": {"Content-Type": "text/html"},
	}


@app.put("/update/:id")
async def update(req):
	try:
		postId = int(req["params"]["id"])
		if DEBUG: print(postId," update")

		data = parse_qs(bytearray(req["body"]).decode("utf-8"))
		title = data["title"][0]

		post = db.post.find_unique(where={'id': postId}, include={'author': True})
		if post.title != title:
			post = db.post.update(where={"id": postId }, include={"author": True}, data={"title": title,"views":{"increment": 1}})
		if DEBUG: print(post)

		return f"<tr> \
		<td>{title}</td> \
		<td>{post.views}</td> \
		<td>{post.author.name}</td> \
		<td>{post.updatedAt}</td> \
		<td> \
		<button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button> \
		<button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button> \
		</td> \
		</tr>"
	except Exception as e:
		raise(e)

@app.put("/delete/:id")
async def delete(req):
	postId = int(req["params"]["id"])
	if DEBUG: print(postId," delete")

	post = db.post.delete(where={'id': postId})
	if post is None:
		return jsonify({"error": "Post doesn't exist."})
	return ""


@app.get("/user")
async def getuser(req):
	try:
		users = db.user.find_many(order={"name":'desc'}, include={"posts": False})
		if DEBUG: print(users)

		return jsonify({
			"data": [user.json() for user in users]
		})
	except Exception as e:
		raise(e)

@app.post("/user")
async def adduser(req):
	try:
		data = parse_qs(bytearray(req["body"]).decode("utf-8"))

		name = data["name"][0]
		if name is None: 
			return jsonify({
				"error": "you need to provide name" 
			})
	
		user = db.user.create( data={ "name": name, })
		return user.json(indent=2)
	except:
		return jsonify({
			"error": "wrong post json params!"
		})


app.start(port=5556, url="0.0.0.0") # url defaults to 127.0.0.1
# python3 /robyn_demo/app.py --processes 4 --workers 4
