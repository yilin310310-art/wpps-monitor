// [RJ] for WPPS.html
// Update: 2026-08-23 10:40:56

var WebInfo = ['Fcst24hPrecipTable','FcstAllPrecipTable'];

var WPPS_WIND_TIME = [];

var WPPS_HTM = {
	'FcstWindTable':'',
	'Fcst24hPrecipTable':'',
	'FcstAllPrecipTable':''
}

var WPPS_MAP = {
	'WindMap_1':{},
	'WindMap_2':{},
	'WindMap_3':{}
};

WPPS_HTM.FcstAllPrecipTable = ''+
    '<!-- Nav tabs -->'+
    '<ul class="nav nav-tabs img-tab" role="tablist">'+
        '<li role="presentation" class="active"><a href="#FcstAllPrecipTable-T" role="tab" data-toggle="tab">預測表</a></li>'+
        '<li role="presentation"><a href="#FcstAllPrecipTable-P" role="tab" data-toggle="tab">預測圖</a></li>'+
    '</ul>'+
    '<!-- Tab panes -->'+
    '<div class="tab-content">'+
        '<div role="tabpanel" class="tab-pane active" id="FcstAllPrecipTable-T">'+
            '<h3 class="sm_subtitle margin-top-20">0822低壓帶及西南風豪雨事件各地區總雨量預測'+
                '<span class="notes">發布時間：115年08月23日10時00分(正報)</span>'+
            '</h3>'+
            '<table class="table table-striped table-rain">'+
                '<thead>'+
                    '<tr>'+
                        '<th rowspan="2" id="PrecAllArea">分區</th>'+
                        '<th colspan="2" id="PrecAll">總雨量(毫米)<br>此為<br class="visible-xs">各區最大累積雨量預測區間<br>自08月23日00時<br class="visible-xs">至8月25日24時止</th>'+
                    '</tr>'+
                    '<tr>'+
                        '<th id="FPAll" headers="PrecAll">平地</th>'+
                        '<th id="MPAll" headers="PrecAll">山區</th>'+
                    '</tr>'+
                '</thead>'+
                '<tbody>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">基隆市</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">臺北市</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">80 - 150</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">新北市</td>'+
                        '<td headers="PrecAll FPAll">200 - 300</td>'+
                        '<td headers="PrecAll MPAll">200 - 300</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">桃園市</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">150 - 250</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">新竹市</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">新竹縣</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">150 - 250</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">苗栗縣</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">150 - 250</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">臺中市</td>'+
                        '<td headers="PrecAll FPAll">100 - 200</td>'+
                        '<td headers="PrecAll MPAll">200 - 400</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">彰化縣</td>'+
                        '<td headers="PrecAll FPAll">100 - 200</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">南投縣</td>'+
                        '<td headers="PrecAll FPAll">100 - 200</td>'+
                        '<td headers="PrecAll MPAll">300 - 500</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">雲林縣</td>'+
                        '<td headers="PrecAll FPAll">150 - 300</td>'+
                        '<td headers="PrecAll MPAll">200 - 350</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">嘉義市</td>'+
                        '<td headers="PrecAll FPAll">150 - 300</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">嘉義縣</td>'+
                        '<td headers="PrecAll FPAll">300 - 500</td>'+
                        '<td headers="PrecAll MPAll">300 - 500</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">臺南市</td>'+
                        '<td headers="PrecAll FPAll">300 - 500</td>'+
                        '<td headers="PrecAll MPAll">300 - 500</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">高雄市</td>'+
                        '<td headers="PrecAll FPAll">400 - 600</td>'+
                        '<td headers="PrecAll MPAll">500 - 700</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">屏東縣</td>'+
                        '<td headers="PrecAll FPAll">500 - 700</td>'+
                        '<td headers="PrecAll MPAll">500 - 800</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">恆春半島</td>'+
                        '<td headers="PrecAll FPAll">400 - 600</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">宜蘭縣</td>'+
                        '<td headers="PrecAll FPAll">200 - 350</td>'+
                        '<td headers="PrecAll MPAll">300 - 500</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">花蓮縣</td>'+
                        '<td headers="PrecAll FPAll">300 - 500</td>'+
                        '<td headers="PrecAll MPAll">400 - 600</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">臺東縣</td>'+
                        '<td headers="PrecAll FPAll">400 - 600</td>'+
                        '<td headers="PrecAll MPAll">400 - 600</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">蘭嶼綠島</td>'+
                        '<td headers="PrecAll FPAll">150 - 300</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">連江縣</td>'+
                        '<td headers="PrecAll FPAll">50 - 100</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">金門縣</td>'+
                        '<td headers="PrecAll FPAll">80 - 150</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="PrecAllArea">澎湖縣</td>'+
                        '<td headers="PrecAll FPAll">150 - 300</td>'+
                        '<td headers="PrecAll MPAll">-</td>'+
                    '</tr>'+
                '</tbody>'+
            '</table>'+
            '<div class="other">'+
                '<p class="note">註</p>'+
                '<ul class="list-unstyled">'+
                    '<li class="datalink"><a href="/Data/typhoon/WPPS/WPPS_WWW_FcstAllPrecipTable.png?T=2026082310" target="_blank" title="檔案 WPPS_WWW_FcstAllPrecipTable.png 點此"><i class="fa fa-download" aria-hidden="true"></i>另存總雨量預測表圖檔</a></li>'+
                    '<li>依據最新數值模式預測降雨量綜合研判，預報具不確定性，請隨時更新預報資訊。</li>'+
                    '<li>預定下次發布時間：115年08月23日13時00分</li>'+
                '</ul>'+
            '</div>'+
        '</div>'+
        '<div role="tabpanel" class="tab-pane" id="FcstAllPrecipTable-P">'+
            '<h3 class="sm_subtitle margin-top-20">總雨量預測圖</h3>'+
            '<div class="row">'+
                '<div class="col-md-12">'+
                    '<img class="img-responsive" src="/Data/typhoon/WPPS/WPPS_REG_FcstAllPrecipImage.png?T=2026082310" alt="總雨量預測圖">'+
                '</div>'+
            '</div>'+
        '</div>'+
    '</div>';
    
WPPS_HTM.Fcst24hPrecipTable = ''+
    '<!-- Nav tabs -->'+
    '<ul class="nav nav-tabs img-tab" role="tablist">'+
        '<li role="presentation" class="active"><a href="#Fcst24hPrecipTable-T" role="tab" data-toggle="tab">預測表</a></li>'+
        '<li role="presentation"><a href="#Fcst24hPrecipTable-P" role="tab" data-toggle="tab">預測圖</a></li>'+
    '</ul>'+
    '<!-- Tab panes -->'+
    '<div class="tab-content">'+
        '<div role="tabpanel" class="tab-pane active" id="Fcst24hPrecipTable-T">'+
            '<h3 class="sm_subtitle margin-top-20">0822低壓帶及西南風豪雨事件各地區24小時雨量預測'+
                '<span class="notes">發布時間：115年08月23日10時00分(正報)</span>'+
            '</h3>'+
            '<table class="table table-striped table-rain">'+
                '<thead>'+
                    '<tr>'+
                        '<th rowspan="2" id="Prec24hArea">分區</th>'+
                        '<th colspan="2" id="Prec24h">24小時雨量(毫米)<br>有效時間：<br class="visible-xs">08月23日14時至08月24日14時</th>'+
                    '</tr>'+
                    '<tr>'+
                        '<th id="FP24h" headers="Prec24h">平地</th>'+
                        '<th id="MP24h" headers="Prec24h">山區</th>'+
                    '</tr>'+
                '</thead>'+
                '<tbody>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">基隆市</td>'+
                        '<td headers="Prec24h FP24h">&lt; 80</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">臺北市</td>'+
                        '<td headers="Prec24h FP24h">50 - 100</td>'+
                        '<td headers="Prec24h MP24h">50 - 100</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">新北市</td>'+
                        '<td headers="Prec24h FP24h">80 - 150</td>'+
                        '<td headers="Prec24h MP24h">80 - 150</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">桃園市</td>'+
                        '<td headers="Prec24h FP24h">&lt; 80</td>'+
                        '<td headers="Prec24h MP24h">80 - 150</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">新竹市</td>'+
                        '<td headers="Prec24h FP24h">&lt; 80</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">新竹縣</td>'+
                        '<td headers="Prec24h FP24h">50 - 100</td>'+
                        '<td headers="Prec24h MP24h">80 - 150</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">苗栗縣</td>'+
                        '<td headers="Prec24h FP24h">50 - 100</td>'+
                        '<td headers="Prec24h MP24h">80 - 150</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">臺中市</td>'+
                        '<td headers="Prec24h FP24h">80 - 150</td>'+
                        '<td headers="Prec24h MP24h">150 - 250</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">彰化縣</td>'+
                        '<td headers="Prec24h FP24h">80 - 150</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">南投縣</td>'+
                        '<td headers="Prec24h FP24h">80 - 150</td>'+
                        '<td headers="Prec24h MP24h">150 - 250</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">雲林縣</td>'+
                        '<td headers="Prec24h FP24h">100 - 190</td>'+
                        '<td headers="Prec24h MP24h">100 - 190</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">嘉義市</td>'+
                        '<td headers="Prec24h FP24h">80 - 150</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">嘉義縣</td>'+
                        '<td headers="Prec24h FP24h">100 - 190</td>'+
                        '<td headers="Prec24h MP24h">100 - 190</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">臺南市</td>'+
                        '<td headers="Prec24h FP24h">200 - 300</td>'+
                        '<td headers="Prec24h MP24h">150 - 300</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">高雄市</td>'+
                        '<td headers="Prec24h FP24h">250 - 400</td>'+
                        '<td headers="Prec24h MP24h">200 - 400</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">屏東縣</td>'+
                        '<td headers="Prec24h FP24h">300 - 400</td>'+
                        '<td headers="Prec24h MP24h">300 - 400</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">恆春半島</td>'+
                        '<td headers="Prec24h FP24h">200 - 340</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">宜蘭縣</td>'+
                        '<td headers="Prec24h FP24h">150 - 250</td>'+
                        '<td headers="Prec24h MP24h">200 - 340</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">花蓮縣</td>'+
                        '<td headers="Prec24h FP24h">200 - 340</td>'+
                        '<td headers="Prec24h MP24h">250 - 400</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">臺東縣</td>'+
                        '<td headers="Prec24h FP24h">200 - 340</td>'+
                        '<td headers="Prec24h MP24h">200 - 340</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">蘭嶼綠島</td>'+
                        '<td headers="Prec24h FP24h">100 - 190</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">連江縣</td>'+
                        '<td headers="Prec24h FP24h">&lt; 50</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">金門縣</td>'+
                        '<td headers="Prec24h FP24h">&lt; 80</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                    '<tr>'+
                        '<td headers="Prec24hArea">澎湖縣</td>'+
                        '<td headers="Prec24h FP24h">100 - 190</td>'+
                        '<td headers="Prec24h MP24h">-</td>'+
                    '</tr>'+
                '</tbody>'+
            '</table>'+
            '<div class="other">'+
                '<p class="note">註</p>'+
                '<ul class="list-unstyled">'+
                    '<li class="datalink"><a href="/Data/typhoon/WPPS/WPPS_WWW_Fcst24hPrecipTable.png?T=2026082310" target="_blank" title="檔案 WPPS_WWW_Fcst24hPrecipTable.png 點此"><i class="fa fa-download" aria-hidden="true"></i>另存24小時雨量預測表圖檔</a></li>'+
                    '<li>依據最新數值模式預測降雨量綜合研判，預報具不確定性，請隨時更新預報資訊。</li>'+
                    '<li>預定下次發布時間：115年08月23日13時00分</li>'+
                '</ul>'+
            '</div>'+
        '</div>'+
        '<div role="tabpanel" class="tab-pane" id="Fcst24hPrecipTable-P">'+
            '<h3 class="sm_subtitle margin-top-20">24小時雨量預測圖</h3>'+
            '<div class="row">'+
                '<div class="col-md-12">'+
                    '<img class="img-responsive" src="/Data/typhoon/WPPS/WPPS_REG_Fcst24hPrecipImage.png?T=2026082310" alt="24小時雨量預測圖">'+
                '</div>'+
            '</div>'+
        '</div>'+
    '</div>';
