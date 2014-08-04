<form  id="maprender" method=post>
    <input type=hidden name="clicked_x" id="clicked_x" value="">
    <input type=hidden name="clicked_y" id="clicked_y" value="">
    <input type=hidden name="iconsection" id="iconsection" value="">
    <input type=hidden name="iconindex" id="iconindex" value="">
    <input type=hidden name="iconname" id="iconname" value="">
</form>

<script>
    function clickHandler(x,y) {
        document.getElementById('clicked_x').value = x;
        document.getElementById('clicked_y').value = y;
        document.getElementById('maprender').submit();
    }
</script>
<script>
    function itemclickHandler(x,y, section, name) {
        document.getElementById('clicked_x').value = x;
        document.getElementById('clicked_y').value = y;
        document.getElementById('iconsection').value = section;
        document.getElementById('iconname').value = name;
        document.getElementById('maprender').submit();
    }
</script>

<script>
    function charclickHandler(x,y, index) {
        document.getElementById('clicked_x').value = x;
        document.getElementById('clicked_y').value = y;
        document.getElementById('iconindex').value = index;
        document.getElementById('maprender').submit();
    }
</script>

</center>

 
<table border=0 width=100%>
<tr>
    <td valign=top>

<table border=1, cellpadding=0, cellspacing=0>
    <tr>
        <td colspan="{{map.max_x + 1}}" bgcolor=lightblue align=center>
            {% if editmode %}
            <table border=1 width=100%>
            <tr>
                <td align=center width=50%>
                <form method=post id="mapload">
                    <select name="loadmap">
                        <option value="New Map">New Map</option>
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
                        Lightradius:<input type=text size=2 name="lightradius" value="{{map.lightradius}}">
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
        <td  bgcolor=lightgray></td>
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
                    <td valign=bottom style="background-image:url(/icon/{{col.core.icon}});background-repeat:repeat;background-size:50px 50px; width:50; height:50" >
                        {% if mapobj.tile(x,y).tiletype() == 'signpost' %}
                        <img src=/icon/icons/blank.png width=50 height=20 align=top
                        title="{{mapobj.tile(x,y).get('/conditional/message', '') }}"
                        onclick="clickHandler({{x}},{{y}})">
                        {% endif %}                           
                    {% else %}
                    <td valign=bottom style="background-image:url(/icon/icons/blank.png);background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                    {% endif %}
                    {% for icontuple in mapobj.tile_icons(x,y,True) %}
                        {% set k = icontuple[0] %}
                        {% set v = icontuple[1] %}
                        {% if not mapobj.tile(x,y).tiletype() == 'shop' %}
                            <img width=25 height=25 src="/icon/{{v}}" title="{{k}}" onclick="clickHandler({{x}},{{y}})" align=left>
                        {% endif %}
                    {% endfor %}
                    {% if charicons %}
                    {% for char in charicons[(x, y)] %}
                        {% set title = char.displayname() %}
                        {% set icon = char.get('/core/icon', '') %}
                        <img width=25 height=25 src="/icon/{{icon}}" title="{{title}}" onclick="clickHandler({{x}},{{y}})" align=left>
                    {% endfor %}
                    {% endif %}
                    <br>
                      {% if editmode or mapobj.tile(x,y).canenter() %}
                        <img src="/icon/icons/page-zoom.png" width=20 height=20 align=top onclick="clickHandler({{x}},{{y}})">
                      {% endif %}
                {% else %}
                    <td valign=top style="background-image:url(/icon/backgrounds/unrevealed.png);background-repeat:repeat;background-size:50px 50px; width:50; height:50" >
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
                    <td height=500 valign=middle style="background-image:url(/icon/{{icon}});background-repeat:repeat;background-size:500px 500px; width:500; height:500">
                     {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'signpost' %}
                       <strong><center><font color=red size=12>
                        {{mapobj.tile(zoom_x,zoom_y).get('/conditional/message', '') }}
                       </font></strong></center>
                    {% endif %}    
                {% else %}
                    <td height=500 valign=bottom style="background-image:url(/icon/icons/blank.png;background-repeat:repeat;background-size:500px 500px; width:500; height:500">
                {% endif %}
                    {% for icontuple in mapobj.tile_icons(zoom_x,zoom_y) %}
                        {% set k = icontuple[0] %}
                        {% set v = icontuple[1] %}
                        {% set section = icontuple[2] %}
                        <img title="{{k}}" src="/icon/{{v}}" align=left onclick="itemclickHandler({{zoom_x}},{{zoom_y}}, '{{section}}', '{{k}}')">
                    {% endfor %}
                    {% if charicons %}
                    {% for char in charicons[(zoom_x, zoom_y)] %}
                        {% set title = char.displayname() %}
                        {% set index = char.index %}
                        {% set icon = char.get('/core/icon', '') %}
                        <img title="{{title}}" src="/icon/{{icon}}" align=left onclick="charclickHandler({{zoom_x}},{{zoom_y}}, '{{index}}')">

                    {% endfor %}
                    {% endif %}
                </td>
            </tr>
            <tr>
                <td>
                    <form method=post>
                        <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                        <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                    {% if editmode %}
                            <select name="load_tile_from_file">
                                {% for tile in tilelist %}
                                    <option value="{{tile}}">{{tile}}</option>
                                {% endfor %}
                            </select>
                            <input type=submit name="loadtilefromfile" value="Load tile from file"><br>
                                {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'signpost' %}
                                    Message:<input type=text size=70 name=message value="{{mapobj.tile(zoom_x,zoom_y).get('/conditional/message', '') }}">
                                    <input type=submit name="signpostmessage" value="Change Signpost">
                                {% endif %}
                            {% if mapobj.tile(zoom_x,zoom_y).canenter() %}
                            <select name="charactername">
                                {% for char in playerlist %}
                                    <option value="{{char}}">{{char}}</option>
                                {% endfor %}
                            </select>
                            <input type=submit name="addchartotile" value="Add character (Will autosave map)"><br>
                            <select name="npcname">
                                {% for char in npclist %}
                                    <option value="{{char}}">{{char}}</option>
                                {% endfor %}
                            </select>                            
                            <input type=submit name="addnpctotile" value="Add NPC">
                            <input type=submit name="removenpcfromtile" value="Remove NPC">
                            <br>
                            <select name="itemname">
                                {% for item in itemlist %}
                                    <option value="{{item}}">{{item}}</option>
                                {% endfor %}
                            </select>                            
                            <input type=submit name="additemtotile" value="Add Item">
                            <input type=submit name="removeitemfromtile" value="Remove Item">
                            <br>
                                {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'link' %}
                                {% set target = mapobj.tile(zoom_x,zoom_y).linktarget() %}
                                Link Map: 
                                <select name=targetmap>
                                    <option value="{{target['mapname']}}">{{target['mapname']}}</option>
                                    {% for tmap in maplist %}
                                    <option value="{{tmap}}">{{tmap}}</option>
                                    {%endfor%}
                                </select>
                                X:<input type=text size=2 name='target_x' value="{{target['x']}}">
                                Y:<input type=text size=2 name="target_y" value="{{target['y']}}">
                                <input type=submit value="Set Target" name="settargetmap">
                                {% endif %}
                            {% endif %}
                    {% else %}
                       {% if mapobj.tile(zoom_x,zoom_y).canenter() %}
                            <input type=submit name="movehere" value="Move Here">
                            <br>
                       {% endif %}
                       {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'link' %}
                            <input type=submit name="followlink" value="Go to next map"><br>
                       {% endif %}
                       {% if mapobj.tile(zoom_x, zoom_y).tiletype() == 'shop' %}
                       {% if packitems %}
                            <select name="itemtosell">
                                {% for item, name, price in packitems %}
                                    <option value={{item}}>{{name}} - {{price}}</option>
                                {% endfor %}
                            </select>
                            <input type=submit name="sellitem" value="Sell Item"><br>
                        {% endif %}
                       {% endif %}
                    {% endif %}
                    </form>
                </td>
            </tr>
            {% if editmode %}
                <tr>
                <script language="javascript" type="text/javascript" src="/js?path=editarea_0_8_2/edit_area/edit_area_full.js"></script>
                    <td>
                        <form method=post>
                            <textarea id="pythonconsole" cols=60 rows=10 name="pythonconsole">#python console</textarea><br>
                            <script language="javascript" type="text/javascript">
                                editAreaLoader.init({
                                    id : "pythonconsole"       // textarea id
                                    ,syntax: "python"           // syntax to be uses for highgliting
                                    ,start_highlight: true      // to display with highlight mode on start-up
                                });
                            </script>
                            <input type=submit value="Run code">
                        </form><br>
                        jsonbox<form method=post>
                            <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                            <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                            <textarea id="jsonbox" cols=60 rows=10 name="jsonbox">{{mapobj.tile(zoom_x,zoom_y)}}</textarea><br>
                            <script language="javascript" type="text/javascript">
                                editAreaLoader.init({
                                    id : "jsonbox"       // textarea id
                                    ,syntax: "python"           // syntax to be uses for highgliting
                                    ,start_highlight: true      // to display with highlight mode on start-up
                                });
                            </script>
                            <input type=submit value="Update tile JSON" name="updatejson">
                        </form>
                    </td>
                </tr>
            {% else %}
                {% if detailview %}
                <tr>
                    <td bgcolor=lightblue>
                        <form method=post>
                            <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                            <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                            <input type=hidden name="detailtype" id="detailtype" value="{{detailtype}}">
                            <input type=hidden name="detailname" id="detailname" value="{{detailname}}">
                            <input type=hidden name="detailindex" id="detailindex" value="{{detailindex}}">
                            {% if detailtype == 'item' %}
                                {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'shop' %}
                                    <input type="submit" name="itemdetail" value="Buy">
                                {% else %}   
                                    <input type="submit" name="itemdetail" value="Pick up">
                                {% endif %}
                            {% else %}  
                                <fieldset>
                                    <legend>Attack options</legend>
                                    {% for option in attackmods %}
                                        <div>
                                            <input type=checkbox name=attackmods value="{{option}}">
                                            <label>{{option}}</label>
                                        </div>
                                    {% endfor %}
                                    <input type=submit name="attack" value="Attack">
                                </fieldset>
                            {% endif %}
                        <br>
                        <ul>
                        {%- for key, value in detailview.items() recursive  %}                       
                          <li>{{ key }}                                                           
                            {%- if value is mapping %}                            
                            <ul>{{ loop(value.items())}}</ul>
                            {% else %}
                                = {{value}}
                            {%- endif %}                                                            
                          </li>                                                                     
                        {%- endfor %}   
                        </ul>
                    </td>
                </tr>
                {% endif %}
                {%endif%}
            </table>
        </table>

    </center>
</td></tr>

<center>