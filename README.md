# KITHUBSys

## これは何？

Discordサーバ管理用Botシステム

## 開発

### 開発環境

- **python**
    - 3.10以降
    - 動作には必要ないが、開発時にあったほうがサジェストとか出るので良い
- **Docker**
    - Docker Composeを利用

### 環境構築

```shell
1. リポジトリをcloneする

git clone git@github.com:act-kithub/KITHUBSys.git

2. プロジェクトディレクトリに移動する

cd KITHUBSys

3. poetryをインストールする

pip install poetry

4. poetryで依存関係をインストールする

make poetry:dev:setup

5. poetry環境に入る

make poetry:shell

6. envファイルをコピーする

make envs:init

7. discord.envにDiscordのBotトークンを設定する

nano envs/discord.env

8. 立ち上げる

make up
```

> [!NOTE]
> ソースの編集は`discord`ディレクトリをルートとしてVSCodeやIDEで開いたほうが楽です
> （ローカルパッケージの名前解決ができません）
> 
> また、discordディレクトリ内にある `pyproject.toml`や `poetry.lock`、 `db`ディレクトリは
> すべてプロジェクトルートにある同名ファイル・ディレクトリのシンボリックリンクです


### 開発に必要そうなコマンド

```shell
> docker composeコマンドを直接叩くときは、
> docker compose -f compose.dev.yml ~~ で
> compose.dev.ymlを指定する

- dockerコンテナを立ち上げ直す
make reload

- Pythonパッケージを追加
make poetry:add group=discord packages="xxx yyy zzz"
※ dbの依存関係に入れたい場合は group=db

- DBのマイグレーションファイルを生成
make db:revision:create NAME="add_column_to_table"
※ db/packages/models.py の編集後に実施

- DBのマイグレーションを実行
make db:migrate
```

