# sound-source-separation-lib
音源の取得とマルチチャネル音源分離

# Install

PyAudioインストール時のエラー対処法　[記事](https://qiita.com/musaprg/items/34c4c1e0e9eb8e8cc5a1)

```
pip install requirements.txt
```

# Record

## マイク情報の表示

チェンネル数のinが1以上のマイクで録音可能

```
python record.py -i
#Index: 0 | Name: DELL U2720QM | ChannelNum: in 0 out 2 | SampleRate: 48000.0
#Index: 1 | Name: MacBook Proのマイク | ChannelNum: in 1 out 0 | SampleRate: 48000.0
```

## 録音開始

midで、使用するマイクロホンのIndexを選択する。

```
python ./app/record.py -f <file_name> -mid <mic_id> -t <sec>
python ./app/record.py -f ./data/test.wav -mid 1 -t 5
```