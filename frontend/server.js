const http = require("http");
const fs = require("fs").promises;
const path = require("path");

const PORT = 3000;

let headerContent = "";

async function loadHeader() {
  try {
    headerContent = await fs.readFile(
      path.join(__dirname, "/views/templates/Navbar.html"),
      "utf-8"
    );
  } catch (err) {
    console.error("Error while loading header:", err);
    headerContent = "<div>Error loading header</div>";
  }
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === "/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok" }));
      return;
    }

    const filePath = getFilePath(req.url);
    const contentType = getContentType(filePath);

    // 画像ファイルの場合はバイナリとして読み込む
    if (contentType.startsWith("image/")) {
      const data = await fs.readFile(filePath);
      res.writeHead(200, {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=31536000",
      });
      res.end(data);
      return;
    }

    const content = await fs.readFile(filePath, "utf-8");
    const renderedContent = content
      .replace(
        '<div id="header_container"></div>',
        `<div id="header_container">${headerContent}</div>`
      )
      .replace(
        '<div id="body_container"></div>',
        `<div id="body_container">${await renderPage(req.url)}</div>`
      )
      .replace(
        '<script id="load_env"></script>',
        `<script>
          window.env = {
            BACKEND_HOST: '${process.env.BACKEND_HOST ?? ""}',
            GAMEPLAY_HOST: '${process.env.GAMEPLAY_HOST ?? ""}',
            GAMEPLAY_WS_HOST: '${process.env.GAMEPLAY_WS_HOST ?? ""}'
          };
        </script>`
      );

    res.writeHead(200, {
      "Content-Type": contentType,
      "Cache-Control": "no-cache",
    });
    res.end(renderedContent);
  } catch (err) {
    console.error("Server error:", err);
    res.writeHead(500, { "Content-Type": "text/plain" });
    res.end("Internal Server Error");
  }
});

const getFilePath = (url) => {
  if (url.startsWith("/public/")) {
    return path.join(__dirname, url);
  }
  return path.join(__dirname, url === "/" ? "index.html" : url);
};

const getContentType = (filePath) => {
  const extname = path.extname(filePath);
  const mimeTypes = {
    ".html": "text/html",
    ".js": "application/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
  };
  return mimeTypes[extname] || "application/octet-stream";
};

const renderPage = async (url) => {
  const pages = {
    "/": "<h1>Welcome to the Home Page</h1>",
    // 他のページを追加可能
  };
  return pages[url] || "<h1>404 - Page Not Found</h1>";
};

loadHeader().then(() => {
  server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
  });
});
