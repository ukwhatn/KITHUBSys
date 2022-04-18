<?php
/*
 * Request Control Map
 *  /_admin
 *      - セッション確認
 *          True: 管理画面
 *          False: Forbidden with Login button
 *  After discord OAuth
 *      - クエリパラメータ確認
 *          code: tokenize, セッション格納, コードなしにリダイレクト
 *          error: セッションに格納された元ページへ
 *  The Others
 *      - 存在確認
 *          True: 表示
 *          False: 404ページへ
 *
 */

/*
 * $_SESSION Structure
 *  DiscordUserObject: DiscordUserObjectクラスオブジェクト(serialized)
 *  latestPath: 最後にアクセスしたページのパス
 *
 */

/*
 * セッションを作成
 */
session_name("TOKEN");
session_start();

/*
 * コンポーネントをinclude
 */
# Staticな関数系
require_once __DIR__ . "/../php/functions.php";
# データクラス系
require_once __DIR__ . "/../php/DataClass.php";
# BladeOne(テンプレートエンジン)
require_once __DIR__ . "/../util/blade.php";
$blade = new Blade();
# Database(PDO利用)
require_once __DIR__ . "/../php/Database.php";
try {
    $DB = new DB();
} catch (InitialConnectException $e) {
    # PDO接続に失敗したら500を返して終わる
    http_response_code(500);
    functions::errorLog($e);
    echo $blade->run("response_code.500", ["code" => "init_db_error"]);
    exit;
}

# Config取得
$rootURI = $DB->getRootURI();

# リクエストパス解析
$parsedRequestURL = parse_url($rootURI . $_SERVER["REQUEST_URI"]);
$pagePath = mb_strtolower($parsedRequestURL["path"]);

# Discord OAuth2 Initialize
require_once __DIR__ . "/../php/Discord.php";
$discordOAuth2Data = $DB->getDiscordOAuthData();
$discordOAuth2 = new DiscordOAuth2(
    $discordOAuth2Data["discord_oauth2_client_id"],
    $discordOAuth2Data["discord_oauth2_client_secret"],
    $rootURI . $discordOAuth2Data["discord_oauth2_redirect_path"]
);

# メソッド判定
if ($_SERVER["REQUEST_METHOD"] === "GET") {
    if (array_key_exists("logout", $_GET)) {
        // logout = true => sessionに保存されたデータを破棄
        unset($_SESSION["DiscordUserObject"]);
        unset($_SESSION["SystemUserObject"]);
        Header("Location: " . $rootURI . $pagePath);
        exit;
        // ↑↑リダイレクトして終了↑↑ //
    }

    if (array_key_exists("error", $_GET) && $_GET["error"] === "access_denied") {
        // OAuthキャンセル/エラー
        if (array_key_exists("latestPath", $_SESSION)) {
            Header("Location: " . $rootURI . $_SESSION["latestPath"]);
        } else {
            Header("Location: " . $rootURI);
        }
        exit;
    }

    if (array_key_exists("code", $_GET)) {
        // code付 = discord認証直後 tokenize前
        try {
            $discordUser = $discordOAuth2->tokenize($_GET["code"]);
            $discordUser->getMe();
            //$DB->updateDiscordUserName($discordUser);
            $_SESSION["DiscordUserObject"] = serialize($discordUser);
            if (array_key_exists("latestPath", $_SESSION)) {
                Header("Location: " . $rootURI . $_SESSION["latestPath"]);
            } else {
                Header("Location: " . $rootURI);
            }
        } catch (DiscordTokenizeException $e) {
            // tokenize失敗
            if (array_key_exists("latestPath", $_SESSION)) {
                Header("Location: " . $rootURI . $_SESSION["latestPath"]);
            } else {
                Header("Location: " . $rootURI);
            }
        }
        exit;
        // ↑↑リダイレクトして終了↑↑ //
    } else {
        // ログインセッション確認
        $discordUser = null;
        $systemUser = null;
        if (array_key_exists("DiscordUserObject", $_SESSION) && array_key_exists("SystemUserObject", $_SESSION)) {
            $discordUser = unserialize($_SESSION["DiscordUserObject"]);
            $systemUser = unserialize($_SESSION["SystemUserObject"]);
        }

        /**
         * 以下通常ページ表示
         */

        # セッションにパスを保存
        $_SESSION["latestPath"] = $pagePath;

        var_dump($_SESSION);

        echo <<<HD
            <a href="{$discordOAuth2->getLoginURL('identify')}">LOGIN</a>
HD;


        exit;
        // ↑↑終了↑↑ //
    }
}

# echo $blade->run("base", ["title" => "testTitle", "siteName" => "site", "content" => "CONTENT"]);