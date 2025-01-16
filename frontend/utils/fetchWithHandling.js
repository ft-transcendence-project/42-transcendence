export async function fetchWithHandling(url, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };

    try {
        const options = {
            method,
            headers,
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            const errorData = await response.json();
            console.error("API Error:", errorData);
            throw new Error(`HTTP Error: ${response.status}`);
        }

        // レスポンスデータをパースして返す
        return await response.json();
    } catch (error) {
        console.error("Fetch Error:", error);
        throw error;
    }
}