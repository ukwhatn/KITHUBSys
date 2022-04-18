@extends("base")

@section("pageTitle") Not Found @endsection

@section("styleSheets")
    @import url("/assets/common/response_code.css");
@endsection

@section("mainContent")
    <div class="nf-wrapper">
        <div class="nf-heading">
            404
        </div>
        <div class="nf-subheading">
            Page Not Found
        </div>
        <div class="nf-description">
            ページが見つかりませんでした<br>
        </div>
        <div class="nf-action-link-wrap">
            <a onclick="history.back(-1)" class="btn btn-dark">前のページへ</a>
            <a href="/" class="btn btn-dark">トップページへ</a>
        </div>
    </div>
@endsection

