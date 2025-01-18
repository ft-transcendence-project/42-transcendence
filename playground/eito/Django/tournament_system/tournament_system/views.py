# tournament/views.py
from django.shortcuts import render


def tournament(request):
    # トーナメントページを表示するロジック（必要に応じてデータを渡す）
    return render(request, "tournament.html")
