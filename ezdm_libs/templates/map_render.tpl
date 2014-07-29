<form  id="maprender" method=post>
    <input type=hidden name="clicked_x" id="clicked_x" value="">
    <input type=hidden name="clicked_y" id="clicked_y" value="">
</form>

<script>
    function clickHandler(x,y) {
        document.getElementById('clicked_x').value = x;
        document.getElementById('clicked_y').value = y;
        document.getElementById('maprender').submit();
    }
</script>

</center>

 
<table border=0 width=100%>
<tr>
    <td>

<table border=1, cellpadding=0, cellspacing=0>
    <tr>
        <td colspan="{{map.max_x + 1}}" bgcolor=lightblue align=center>
            {% if editmode %}
            <table border=1 width=100%>
            <tr>
                <td align=center width=50%>
                <form method=post id="mapload">
                    <select name="loadmap">
                        {% for mapitem in maplist %}
                            <option value="{{mapitem}}">{{mapitem}}</option>
                        {% endfor %}
                    </select>
                    <input type=submit value="Load Map">
                </form>
                </td><td align=center>
                <form method=post id="mapsave">Map name:
                    <input type=text name="mapname" value="{{map.name}}">
                    {% if map.name == 'New Map' %}
                        Max X:<input type=text size=2 name="max_x" value="{{map.max_x}}">
                        Max Y:<input type=text size=2 name="max_y" value="{{map.max_y}}">
                    {%endif%}
                    <input type=submit name="savemap" value="Save Map">
                </form>
                </td>
            </tr>
            </table>
            {% else %}
                <center><strong>{{map.name}}
                </strong></center>
            {%endif %}
        </td>
    </tr>
    <tr>
        <td bgcolor=lightgray></td>
        {% for a in range (0,map.max_x) %}
            <td bgcolor=lightgray>{{a}}</td>
        {% endfor %}
    </tr>
    {% for row in map.tiles%}
        {% set y = loop.index - 1 %}
        <tr>
            <td bgcolor=lightgray>{{y}}</td>
            {% for col in row %}
                {% set x = loop.index - 1%}
                {% if editmode or (col.core and col.core.revealed) %}
                    {% if col.core and col.core.icon %}
                    <td valign=bottom style="background-image:url(/icon/{{col.core.icon}});background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                    {% else %}
                    <td valign=bottom style="background-image:url(/icon/icons/blank.png);background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                    {% endif %}
                    {% for k,v in mapobj.tile_icons(x,y).items() %}
                        <img width=20 height=20 src="/icon/{{v}}" align=left>
                    {% endfor %}<br>
                      {% if editmode or col.conditional and col.conditional.canenter %}
                        <input type=button onclick="clickHandler({{x}},{{y}})" value="+">
                      {% endif %}
                {% else %}
                    <td valign=bottom style="background-image:url(/icon/backgrounds/unrevealed.png);background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                {% endif %}
                    </td>
            {% endfor %}
        </tr>
    {% endfor %}
</table>

</td><td valign=top>
    <center>
        <table border=1 width=500>
            <tr>
                <td bgcolor=lightblue align=center>Zoom  {{zoom_x}}x{{zoom_y}}</td>
            </tr>
            <tr>
                {% set tile = map.tiles[zoom_y][zoom_x] %}
                {% if tile.core %}
                    {% set icon = tile.core.icon %}
                    <td height=500 valign=bottom style="background-image:url(/icon/{{icon}});background-repeat:repeat;background-size:500px 500px; width:500; height:500">
                {% else %}
                    <td height=500 valign=bottom style="background-image:url(/icon/icons/blank.png;background-repeat:repeat;background-size:500px 500px; width:500; height:500">
                {% endif %}
                    {% for k,v in mapobj.tile_icons(zoom_x,zoom_y).items() %}
                        <img src="/icon/{{v}}" align=left>
                    {% endfor %}
                </td>
            </tr>
            <tr>
                <td>
                    <form method=post>
                    {% if editmode %}
                            <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                            <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                            <select name="load_tile_from_file">
                                {% for tile in tilelist %}
                                    <option value="{{tile}}">{{tile}}</option>
                                {% endfor %}
                            </select>
                            <input type=submit name="loadtilefromfile" value="Load tile from file"><br>
                            <select name="charactername">
                                {% for char in charlist %}
                                    <option value="{{char}}">{{char}}</option>
                                {% endfor %}
                            </select>
                            <input type=submit name="addchartotile" value="Add character to tile"><br>
                    {% else %}
                       Campaign Mode Goes Here
                    {% endif %}
                    </form>
                </td>
            </tr>
            {% if editmode %}
                <tr>
                <script language="javascript" type="text/javascript" src="/js?path=editarea_0_8_2/edit_area/edit_area_full.js"></script>
                    <td>
                        <form method=post>
                            <textarea id="pythonconsole" cols=60 rows=10 name="pythonconsole">#Enter python commands here to manipulate the map fast</textarea><br>
                            <script language="javascript" type="text/javascript">
                                editAreaLoader.init({
                                    id : "pythonconsole"       // textarea id
                                    ,syntax: "python"           // syntax to be uses for highgliting
                                    ,start_highlight: true      // to display with highlight mode on start-up
                                });
                            </script>
                            <input type=submit value="Run code">
                        </form>
                    </td>
                </tr>
                {%endif%}
            </table>
        </table>

    </center>
</td></tr>

<center>