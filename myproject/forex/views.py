from django.shortcuts import render
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import japanize_matplotlib
import io
import base64
from django.http import HttpResponseBadRequest
from datetime import datetime


#ドル円相場と日経平均株価のプログラミング
def index(request):
    # インデックスページをレンダリングする
    return render(request, 'index.html')

def result(request):
    # フォームから日付を取得
    start_date = request.GET.get('start') # 開始日を取得
    end_date = request.GET.get('end') # 終了日を取得
    
    # 開始日と終了日のチェック
    if not start_date or not end_date:
        # 日付が入力されていない場合はエラーを返す
        return HttpResponseBadRequest("開始日と終了日を指定してください。")

    try:
        # ドル円のティッカーシンボル
        usd_jpy_ticker = "JPY=X"
        
        # 日経平均株価のティッカーシンボル
        nikkei_ticker = "^N225"

        # ドル円のデータをダウンロード
        usd_jpy_data = yf.download(usd_jpy_ticker, start=start_date, end=end_date)

        # 日経平均株価のデータをダウンロード
        nikkei_data = yf.download(nikkei_ticker, start=start_date, end=end_date)


        # グラフの作成
        usd_jpy_plot_url = create_plot(usd_jpy_data, 'USD/JPY', 'ドル円為替レートの終値')
        nikkei_plot_url = create_plot(nikkei_data, 'Nikkei 225', '日経平均株価の終値')

        # ドル円の最高値と最低値の計算
        usd_jpy_max_high = usd_jpy_data['High'].max() # ドル円の最高値
        usd_jpy_max_high_date = usd_jpy_data['High'].idxmax() # ドル円の最高値の日付
        usd_jpy_min_low = usd_jpy_data['Low'].min()  # ドル円の最低値
        usd_jpy_min_low_date = usd_jpy_data['Low'].idxmin() # ドル円の最低値の日付

        # 日経平均株価の最高値と最低値の計算
        nikkei_max_high = nikkei_data['High'].max() # 日経平均株価の最高値
        nikkei_max_high_date = nikkei_data['High'].idxmax() # 日経平均株価の最高値の日付
        nikkei_min_low = nikkei_data['Low'].min() # 日経平均株価の最低値
        nikkei_min_low_date = nikkei_data['Low'].idxmin() # 日経平均株価の最低値の日付

    except Exception as e:
        # エラーが発生した場合はエラーメッセージを返す
        return HttpResponseBadRequest(f"データ取得中にエラーが発生しました: {str(e)}")
    
    # 結果ページをレンダリングし、計算結果とグラフを表示する
    return render(request, 'result.html', {
        'usd_jpy_max_high': usd_jpy_max_high, # ドル円の最高値の計算結果をレンダリング
        'usd_jpy_max_high_date': usd_jpy_max_high_date.date(), # ドル円の最高値の日付をレンダリング
        'usd_jpy_min_low': usd_jpy_min_low, # ドル円の最低値の計算結果をレンダリング
        'usd_jpy_min_low_date': usd_jpy_min_low_date.date(), # ドル円の最低値の日付をレンダリング
        'usd_jpy_plot_url': usd_jpy_plot_url, # ドル円相場のグラフをレンダリング
        'nikkei_max_high': nikkei_max_high, # 日経平均株価の最高値の計算結果をレンダリング
        'nikkei_max_high_date': nikkei_max_high_date.date(), # 日経平均株価の最高値の日付をレンダリング
        'nikkei_min_low': nikkei_min_low, # 日経平均株価の最低値の計算結果をレンダリング
        'nikkei_min_low_date': nikkei_min_low_date.date(), # 日経平均株価の最低値の日付をレンダリング
        'nikkei_plot_url': nikkei_plot_url # 日経平均株価のグラフをレンダリング
    })

#ドル円相場と日経平均株価のグラフを作成する関数
def create_plot(data, label, title):
    plt.figure(figsize=(10, 5)) # グラフのサイズを設定
    plt.plot(data['Close'], label=label) # 終値のラインをプロット
    plt.scatter(data['High'].idxmax(), data['High'].max(), color='r', label='Max High', zorder=5) # 最高値のポイントをプロット
    plt.scatter(data['Low'].idxmin(), data['Low'].min(), color='g', label='Min Low', zorder=5) # 最低値のポイントをプロット
    plt.text(data['High'].idxmax(), data['High'].max(), f'{data["High"].max():.2f}', color='r', fontsize=12, ha='center') # 最高値をグラフ上に表示
    plt.text(data['Low'].idxmin(), data['Low'].min(), f'{data["Low"].min():.2f}', color='g', fontsize=12, ha='center') # 最低値をグラフ上に表示
    plt.title(title) #タイトルを設定
    plt.xlabel('日付') #X軸のラベルを設定
    plt.ylabel('終値（円）') #Y軸のラベルを設定
    plt.legend() #凡例を表示
    plt.grid(True) #グリッド線の追加
    buf = io.BytesIO() #描画のためのバッファを作成
    plt.savefig(buf, format='png') # バッファにグラフを保存
    buf.seek(0) # バッファの位置を先頭に戻す
    plot_url = base64.b64encode(buf.getvalue()).decode('utf-8') # バッファの内容をBase64でエンコード
    buf.close() # バッファを閉じる
    plt.close() # グラフを閉じる
    return plot_url # エンコードしたグラフのURLを返す

#個別銘柄のプログラミング
def individual_search(request):
    # individual_search.html テンプレートをレンダリングして返すシンプルなビュー関数
    return render(request, 'individual_search.html')

def individual_result(request):
    # フォームからティッカーシンボルと日付を取得
    ticker = request.GET.get('ticker', None)
    start_date = request.GET.get('start', None)
    end_date = request.GET.get('end', None)

    # フォーム入力の検証
    if not ticker or not start_date or not end_date:
        return render(request, 'individual_result.html', {
            'error': 'ティッカーシンボルと日付を正しく入力してください。'
        })

    # ティッカーシンボルに .T を追加
    ticker += ".T"

    # 日付形式の検証
    try:
        # 文字列を datetime オブジェクトに変換し、正しい日付形式をチェック
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        # 日付形式が間違っている場合のエラーハンドリング
        return render(request, 'individual_result.html', {
            'error': '日付形式が正しくありません。YYYY-MM-DDの形式で入力してください。'
        })
    
    # 開始日が終了日より前であるかの検証
    if start_date >= end_date:
        return render(request, 'individual_result.html', {
            'error': '開始日は終了日より前である必要があります。'
        })

    try:
        # yfinance を使用して銘柄のデータをダウンロード
        stock_data = yf.download(ticker, start=start_date, end=end_date)

        if stock_data.empty:
            # ダウンロードされたデータが空の場合のエラーハンドリング
            return render(request, 'individual_result.html', {
                'error': '指定した日付範囲ではデータが見つかりませんでした。'
            })

        # 必要な列名を確認
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            # 必要なデータが欠けている場合のエラーハンドリング
            return render(request, 'individual_result.html', {
                'error': f'データに必要な列が見つかりません: {", ".join(missing_columns)}'
            })

        # 現在の株価データを取得
        stock_info = yf.Ticker(ticker)
        current_price = stock_info.info.get('currentPrice', 'N/A')
        company_name = stock_info.info.get('longName', 'N/A')
        dividend_yield = stock_info.info.get('dividendYield', 0) * 100

        # 銘柄のローソク足チャートを作成
        stock_plot_url = create_candle_plot(stock_data, ticker)

        # 結果をレンダリング
        return render(request, 'individual_result.html', {
            'ticker': ticker,
            'longName': company_name,
            'current_price': f"{current_price:.2f} 円" if current_price != 'N/A' else "N/A",
            'dividend_yield': f"{dividend_yield:.2f} %" if dividend_yield != 0 else "N/A",
            'stock_plot_url': stock_plot_url
        })

    except Exception as e:
        # その他の例外のハンドリング
        return render(request, 'individual_result.html', {
            'error': f'データ取得中にエラーが発生しました: {str(e)}'
        })

def create_candle_plot(data, ticker):
    # 必要な列名を確認し、データが存在することを確認
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if data.empty or not all(col in data.columns for col in required_columns):
        raise ValueError(f"{ticker} のデータが不足しているか、列名が間違っています。")

    # mplfinanceが必要とする形式のDataFrameにデータをリネーム
    data = data.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    # ボリンジャーバンドの計算
    data['SMA20'] = data['close'].rolling(window=20).mean()  # 20日移動平均
    data['SMA50'] = data['close'].rolling(window=50).mean()  # 50日移動平均
    data['STD'] = data['close'].rolling(window=20).std()  # 標準偏差
    data['Upper Band'] = data['SMA20'] + (data['STD'] * 2)  # 上部バンド
    data['Lower Band'] = data['SMA20'] - (data['STD'] * 2)  # 下部バンド

    # 描画のためのバッファを作成
    buf = io.BytesIO()

    # mplfinance スタイル設定
    mpf_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.family': 'IPAexGothic'})

    # 追加プロットとして移動平均線とボリンジャーバンドを設定
    apds = [
        mpf.make_addplot(data['SMA20'], color='orange', linestyle='-', label='SMA20'),
        mpf.make_addplot(data['SMA50'], color='green', linestyle='-', label='SMA50'),
        mpf.make_addplot(data['Upper Band'], color='blue', linestyle='--', label='Upper Band'),
        mpf.make_addplot(data['Lower Band'], color='red', linestyle='--', label='Lower Band')
    ]

    # ローソク足チャートに移動平均線と出来高を加えて描画
    try:
        mpf.plot(data, type='candle', style=mpf_style, title=f'{ticker} のローソク足チャート',
                ylabel='価格（円）', addplot=apds, volume=True, savefig=buf)
    except ValueError as ve:
        raise ValueError(f'プロット作成中にエラーが発生しました: {str(ve)}')

    # バッファの位置を先頭に戻す
    buf.seek(0)

    # バッファから画像データを取得し、base64エンコード
    stock_plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')

    # バッファを閉じる
    buf.close()

    # エンコードしたグラフのURLを返す
    return stock_plot_url 