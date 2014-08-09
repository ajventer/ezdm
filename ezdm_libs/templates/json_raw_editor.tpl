<script language="javascript" type="text/javascript" src="/js?path=editarea_0_8_2/edit_area/edit_area_full.js"></script>
<form method=post>
 <textarea style="width:100%; height: 100%" name="json" id="json">{{json}}</textarea>
<script language="javascript" type="text/javascript">
editAreaLoader.init({
    id : "json"       // textarea id
    ,syntax: "python"           // syntax to be uses for highgliting
    ,start_highlight: true      // to display with highlight mode on start-up
});
</script>
<input type=submit name="saveraw" value="Save">
</form>