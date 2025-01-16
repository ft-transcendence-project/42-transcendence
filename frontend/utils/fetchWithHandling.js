export async function fetchWithHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Fetch error:", errorData);
            throw new Error(`HTTP Error: ${response.status}`);
        }

        // レスポンスを JSON として解析
        return response;
    } catch (error) {
        console.error("An error occurred during fetch:", error.message);
        throw error; // 必要に応じて呼び出し元にエラーを再スロー
    }
}
