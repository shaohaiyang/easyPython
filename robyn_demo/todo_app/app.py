from robyn import Robyn, serve_file, serve_html, jsonify, WebSocket
from robyn.robyn import Response, Request
from robyn.templating import JinjaTemplate
from urllib.parse import parse_qs
from prisma import Prisma
from os import path
import asyncio

DEBUG=True

app = Robyn(__file__)
websocket = WebSocket(app, "/webst")
current_dir = path.dirname(__file__)
jinja_template = JinjaTemplate(path.join(current_dir, "templates"))

db = Prisma(auto_register=True)

@app.startup_handler
async def startup_handler() -> None:
  await db.connect()


@app.shutdown_handler
async def shutdown_handler() -> None:
  if db.is_connected():
    await db.disconnect()


@app.get("/")
@app.get("/post")
async def head():
  try:
    #posts = await db.post.query_raw('''select * from Post order by title desc''')
    posts = await db.post.find_many( order={"title":'asc'}, include={"author": True} )

    context = {
      "framework": "Robyn",
      "templating_engine": "Jinja2",
      "data": posts
    }
    if DEBUG: print(context)

    response = jinja_template.render_template(template_name="index.html", **context)
    return response
  except Exception as e:
    raise(e)


@app.post("/submit")
async def addpost(request: Request):
  data = parse_qs(request.body) # (bytearray(req.get("body")).decode("utf-8")) unused

  title = data.get("title")[0]
  author = data.get("author")[0]

  if title is None or author is None:
    return jsonify({
      "error": "you need to provide title and author!"
    })

  user = await db.user.find_first(where={'name': author})
  if user is None:
    user = await db.user.create(
      data={
        "name": author,
      }
    )

  post = await db.post.create(
    data={
      'title': title,
      'authorId': user.id,
    }
  )
  if DEBUG: print("post <", data, " -> ", title, author, post.id)

  response = f"""<tr>
    <td>{post.title}</td>
    <td>{post.views}</td>
    <td>{author}</td>
    <td>{post.updatedAt}</td>
    <td>
    <button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
    <button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
    </td>
    </tr>"""
  return response


@app.get("/view/:id")
async def getpost(request: Request):
  try:
    postId = int(request.path_params.get("id")) #(req.get("path_params").get("id")) unused
    if DEBUG: print(postId, "view")

    post = await db.post.find_unique(where={'id': postId}, include={'author': True})
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
async def edit(request: Request):
  postId = int(request.path_params.get("id"))
  if DEBUG: print(postId," edit")

  post = await db.post.find_unique(where={'id': postId}, include={'author': True})
  if DEBUG: print(post)

  response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get='/post/{post.id}' hx-swap='outerHTML'>
    <td><input name='title' value='{post.title}'/></td>
    <td>{post.views}</td>
    <td>{post.author.name}</td>
    <td>{post.updatedAt}</td>
    <td>
      <button class='btn btn-info' hx-get='/view/{post.id}'> Cancel </button>
      <button class='btn btn-primary' hx-put='/update/{post.id}' hx-include='closest tr'> Save </button>
    </td>
    </tr>"""
  return response


@app.put("/update/:id")
async def update(request: Request):
  try:
    postId = int(request.path_params.get("id"))
    if DEBUG: print(postId," update")

    data = parse_qs(request.body)
    title = data.get("title")[0]

    post = await db.post.find_unique(where={'id': postId}, include={'author': True})
    if post.title != title:
      post = await db.post.update(where={"id": postId }, include={"author": True}, data={"title": title,"views":{"increment": 1}})
    if DEBUG: print(post)

    response = f"""
    <tr>
    <td>{title}</td>
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

@app.put("/delete/:id")
async def delete(request: Request):
  postId = int(request.path_params.get("id"))
  if DEBUG: print(postId," delete")

  post = await db.post.delete(where={'id': postId})
  if post is None:
    return jsonify({"error": "Post doesn't exist."})
  return ""

# simple user demo
@app.get("/user")
async def getuser(request: Request):
  try:
    users = await db.user.find_many(order={"name":'desc'}, include={"posts": False})
    if DEBUG: print(users)

    return jsonify({
      "data": [user.json() for user in users]
    })
  except Exception as e:
    raise(e)

@app.post("/user")
async def adduser(request: Request):
  try:
    data = parse_qs(request.body)

    name = data.get("name")[0]
    if name is None:
      return jsonify({
        "error": "you need to provide name"
      })

    user = await db.user.create(data={"name": name,})
    return user.json(indent=2)
  except:
    return jsonify({
      "error": "wrong post json path_params!"
    })
###########################################
i = -1
# simple websocket demo
@websocket.on("message")
def connect():
  global i
  i += 1
  if i == 0:
    return "Hello ?"
  elif i == 1:
    return "Who are u?"
  elif i == 2:
    return "haha, I'm shy."
  elif i == 3:
    i = -1
    return "again!"

@websocket.on("close")
def close():
  return "Goodbye world, from ws"

@websocket.on("connect")
def message():
  return "Hello world, from ws"
###########################################
if __name__ == "__main__":
  app.start(port=8080, host="0.0.0.0") # host defaults to 127.0.0.1
