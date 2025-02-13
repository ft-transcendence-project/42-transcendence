export async function fetchHtml(url) {
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json", // デフォルトのヘッダー
    },
  };

  try {
    // fetchを実行
    const response = await fetch(url, defaultOptions);

    // エラーハンドリング
    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error:", errorData);
      throw new Error(`HTTP Error: ${response.status}`);
    }

    console.log("API Success:", response);
    return await response.text();
  } catch (error) {
    console.error("Fetch Error:", error);
    return `<h1 data-i18n="common:page_not_found">Page not found.</h1>`;
  }
}
