from socketify import App, AppOptions, AppListenOptions
from prisma import Prisma
from urllib.parse import parse_qs
from jinja2_templates import Jinja2Template

DEBUG=True

app = App(lifespan=False)
app.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))
router = app.router()

db = Prisma(auto_register=True)

@app.on_start
async def on_start():
  print("start!")
  await db.connect()

@app.on_shutdown
async def on_shutdown():
  print("shutdown!")
  if db.is_connected():
    await db.disconnect()


@router.get("/")
async def home(res, req):
  if not db.is_connected(): await db.connect()
  posts = await db.post.find_many( order={"title":'desc'}, include={"author": True} )
  context = {
        "framework": "Robyn",
        "templating_engine": "Jinja2",
        "data": posts
  }
  res.render("index.html", **context)


@router.post("/submit")
async def addpost(res, req):
  # we can check the Content-Type to accept multiple formats
  content_type = req.get_header("content-type")

  if content_type == "application/json":
    data = await res.get_json()
  elif content_type == "application/x-www-form-urlencoded":
    data = await res.get_form_urlencoded()
  else:
    data = await res.get_text()
  data = parse_qs(data)

  title = data.get("title")[0]
  author = data.get("author","shan")[0]
  if DEBUG: print("post <", data, " -> ", title, author)

  if title is None or author is None:
    res.end("Error: Need to provide title and author!")
 
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
  if DEBUG: print("post <", data)
 
  response = f"""<tr>
                <td>{post.title}</td>
                <td>{author}</td>
                <td>{post.views}</td>
                <td>{post.updatedAt}</td>
                <td>
                <button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
                <button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
                </td>
                </tr>"""
  res.end(response)


@router.put("/delete/:id")
async def delete(res, req):
  postId = int( req.get_parameter(0) )
  if DEBUG: print(postId," delete")
 
  post = await db.post.delete(where={'id': postId})
  if post is None:
    res.end("Error: Post doesn't exist!")
  res.end("")


@router.put("/edit/:id")
async def edit(res, req):
  postId = int( req.get_parameter(0) )
  if DEBUG: print(postId," edit")
 
  post = await db.post.find_unique(where={'id': postId}, include={'author': True})
  if DEBUG: print(post)
 
  response = f"""
                <tr hx-trigger='cancel' class='editing' hx-get='/post/{post.id}' hx-swap='outerHTML'>
                <td><input name='title' value='{post.title}'/></td>
                <td>{post.author.name}</td>
                <td>{post.views}</td>
                <td>{post.updatedAt}</td>
                <td>
                        <button class='btn btn-info' hx-get='/view/{post.id}'> Cancel </button>
                        <button class='btn btn-primary' hx-put='/update/{post.id}' hx-include='closest tr'> Save </button>
                </td>
    </tr>"""
  res.end(response)


@router.get("/view/:id")
async def getpost(res, req):
  try:
    postId = int( req.get_parameter(0) )
    if DEBUG: print(postId," view")
 
    post = await db.post.find_unique(where={'id': postId}, include={'author': True})
    if post is None:
      res.end("Error: Post doesn't exist!")
    else:
      if DEBUG: print(post)
 
    response = f"""<tr>
                <td>{post.title}</td>
                <td>{post.author.name}</td>
                <td>{post.views}</td>
                <td>{post.updatedAt}</td>
                <td>
                <button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
                <button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
                </td>
                </tr>"""
    res.end(response)
  except Exception as e:
    raise(e)
 

@router.put("/update/:id")
async def update(res, req):
  try:
    postId = int( req.get_parameter(0) )
    if DEBUG: print(postId," update")
 
    content_type = req.get_header("content-type")

    if content_type == "application/json":
      data = await res.get_json()
    elif content_type == "application/x-www-form-urlencoded":
      data = await res.get_form_urlencoded()
    else:
      data = await res.get_text()
    print(data)
    data = parse_qs(data)
    title = data.get("title")[0]
 
    post = await db.post.find_unique(where={'id': postId}, include={'author': True})
    if post.title != title:
      post = await db.post.update(where={"id": postId }, include={"author": True}, data={"title": title,"views":{"increment": 1}})
      if DEBUG: print(post)
 
    response = f"""
          <tr>  
                <td>{title}</td>
                <td>{post.author.name}</td>
                <td>{post.views}</td>
                <td>{post.updatedAt}</td>
                <td>
                <button class='btn btn-warning' hx-put='/edit/{post.id}'> Edit </button>
                <button class='btn btn-danger' hx-put='/delete/{post.id}' hx-confirm='Are you sure?'> Delete </button>
                </td>
                </tr>"""
    res.end(response)
  except Exception as e:
    raise(e)
 
###########################################
if __name__ == "__main__":
  app.listen(
    AppListenOptions(port=8080, host="0.0.0.0"),
    lambda config: print( "Listening on port http://%s:%d now\n" % (config.host, config.port))
  ).run()
