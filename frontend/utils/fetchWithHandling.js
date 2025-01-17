export async function fetchWithHandling(url, options = {}, errorMessage = "") {
    const defaultOptions = {
        method: "GET",
        headers: {
            "Content-Type": "application/json",  // デフォルトのヘッダー
        },
    };

    // オプションをマージ
    const finalOptions = {
        ...defaultOptions,
        ...options,
    };

    if (options.body) {
        finalOptions.body = JSON.stringify(options.body);
    }

    try {
        // fetchを実行
        const response = await fetch(url, finalOptions);

        // エラーハンドリング
        if (!response.ok) {
            const errorData = await response.json();
            console.error("API Error:", errorData);
            throw new Error(`HTTP Error: ${response.status}`);
        }

        console.log("API Success:", response);
        return response;
    } catch (error) {
        console.error("Fetch Error:", error);
        if (errorMessage) {
            alert(i18next.t(errorMessage));
        }
        return null;
    }
}
