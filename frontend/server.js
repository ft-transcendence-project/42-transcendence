const http = require("http");
const fs = require("fs").promises;
const path = require("path");

const HOST_IP = process.env.HOST_IP;
const PORT = 3000;

let headerContent = "";
let footerContent = "";

async function loadTemplate(filePath, fallbackContent) {
  try {
    return await fs.readFile(path.join(__dirname, filePath), "utf-8");
  } catch (err) {
    console.error(`Error while loading template (${filePath}):`, err);
    return fallbackContent;
  }
}

async function loadTemplates() {
  headerContent = await loadTemplate(
    "/views/templates/Navbar.html",
    "<div>Error loading header</div>",
  );
  footerContent = await loadTemplate(
    "/views/templates/Footer.html",
    "<div>Error loading footer</div>",
  );
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
        `<div id="header_container">${headerContent}</div>`,
      )
      .replace(
        '<div id="body_container"></div>',
        `<div id="body_container">${await renderPage(req.url)}</div>`,
      )
      .replace(
        '<div id="footer_container"></div>',
        `<div id="footer_container">${footerContent}</div>`,
      )
      .replace(
        '<script id="load_env"></script>',
        `<script>
          window.env = {
            ACCOUNT_HOST: '${process.env.ACCOUNT_HOST ?? ""}',
            GAMEPLAY_HOST: '${process.env.GAMEPLAY_HOST ?? ""}',
            GAMEPLAY_WS_HOST: '${process.env.GAMEPLAY_WS_HOST ?? ""}',
            TOURNAMENT_HOST: '${process.env.TOURNAMENT_HOST ?? ""}'
          };
        </script>`,
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
  return path.join(
    __dirname,
    url === "/" ? "/views/templates/index.html" : url,
  );
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

loadTemplates().then(() => {
  server.listen(PORT, () => {
    console.log(`Server is running on http://${HOST_IP}:${PORT}`);
  });
});
