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
{% set minwidth = (map.max_x + 2) * 50 %}

<div style="vertical-align: top; background-color: #ccffcc; border: 3px solid; display: table-row;"> 

<div style="vertical-align: top; background-color: #ADD6FF; border: 3px solid; display: table-cell; min-width: {{minwidth}}">        
    {% if editmode %}
        <div style="vertical-align: top; background-color: #ccffcc; border: 3px solid;">
            <div style="vertical-align: top; background-color: #ccffcc; border: 3px solid; display: table-row;">
                <div style="background-color: #aaffcc; border: 2px solid; display: table-cell;  ">
                    <form method=post id="mapload">
                        <select name="loadmap">
                            <option value="New Map">New Map</option>
                            {% for mapitem in maplist %}
                                <option value="{{mapitem}}">{{mapitem}}</option>
                            {% endfor %}
                        </select>
                        <input type=submit value="Load Map">
                    </form>
                </div>
                <div style="vertical-align: top; background-color: #aaffcc; border: 2px solid; display: table-cell;  ">
                    <form method=post id="mapsave">Map name:
                        <input type=text name="mapname" value="{{map.name}}">
                        {% if map.name == 'New Map' %}
                            Max X:<input type=text size=2 name="max_x" value="{{map.max_x}}">
                            Max Y:<input type=text size=2 name="max_y" value="{{map.max_y}}">
                            Lightradius:<input type=text size=2 name="lightradius" value="{{map.lightradius}}">
                        {%endif%}
                        <input type=submit name="savemap" value="Save Map">
                    </form>
                </div>
            </div>
        </div>
    {% else %}
        <form method=post>
        <lable><strong>{{map.name}}
        </strong></lable><input type=submit value="Attack Roll Grid" name="combatgrid"></form>
    {%endif %}
    <div style="vertical-align: top; background-color: #ADD6FF; border: 3px solid; display: table-row">            
        <div style="background-color:#ccffcc; border: 1px solid; display: table-cell"></div>
        {% for a in range (0,map.max_x) %}
            <div style="background-color: #ccffcc;  border: 1px solid; display: inline; float:left; width: 50px">{{a}}</div>
        {% endfor %}
    </div>
    {% for row in map.tiles%}
        {% set y = loop.index - 1 %}
        <div  style="vertical-align: top; background-color: #ccffcc; border: 3px solid; display: table-row;">    
            <div style="border: 1px solid; vertical-align: top; background-color: #ccffcc; display: table-cell;">{{y}}</div>
            {% for col in row %}
                {% set x = loop.index - 1%}
                {% if editmode or (col.core and col.core.revealed) %}
                    {% if col.core and col.core.icon %}
                        <div onclick="clickHandler({{x}},{{y}})" style="overflow: hidden; border: 1px solid; display: inline; background-image:url(/icon/{{col.core.icon}});background-size:50px 50px; width:50px; height:50px; max-height: 50px; max-width: 50px; float: left" >                         
                    {% else %}
                        <div onclick="clickHandler({{x}},{{y}})" style="overflow: hidden; border: 1px solid;  display: inline; background-image:url(/icon/icons/blank.png);background-size:50px 50px; width:50px; height:50px; max-height: 50px; max-width: 50px; float: left" >
                    {% endif %}
                    {% for icontuple in mapobj.tile_icons(x,y,True) %}
                        {% set k = icontuple[0] %}
                        {% set v = icontuple[1] %}
                        {% if not mapobj.tile(x,y).tiletype() == 'shop' %}
                            <img  width=22 height=22 src="/icon/{{v}}" title="{{k}}" >
                        {% endif %}
                    {% endfor %}
                    {% if charicons %}
                        {% for idx in charicons[(x, y)] %}
                            {% set char = campaign.characterlist[idx] %}
                            {% if char %}   
                                {% set title = char.displayname() %}
                                {% set icon = char.get('/core/icon', '') %}
                                <img width=22 height=22 src="/icon/{{icon}}" title="{{title}}" >
                            {% endif %}
                        {% endfor %}
                    {% endif %}
                {% else %}
                    <div  style="vertical-align: top; border: 1px solid;  display: inline; background-image:url(/icon/backgrounds/unrevealed.png);background-repeat:repeat;background-size:50px 50px; width:50px; height:50px; max-width: 50px; max-height: 50px; float: left" >
                {% endif %}
                    </div>
            {% endfor %}
        </div>
    {% endfor %}
</div>


 <div style="vertical-align: top; border: 3px solid; #ccffcc; min-width: 500;">
    <div style="vertical-align: top; background-color: #ADD6FF; display: table-row;">
         <div style="vertical-align: top; border: 1px solid; background-color: #ADD6FF; display: table-cell;">
            <strong>Zoom  {{zoom_x}}x{{zoom_y}}</strong>
        </div>
    </div>
    <div style="vertical-align: top; border: 1px solid; background-color:#ccffcc; display: table-row;">
        {% set tile = map.tiles[zoom_y][zoom_x] %}
        {% if tile.core %}
        {% set icon = tile.core.icon %}
        <div style="vertical-align: top; border: 1px solid; background-image:url(/icon/{{icon}});background-repeat:repeat;background-size:500px 500px; width:500; height:500 ; display:table-cell">
        {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'signpost' %}
            <strong>
                <center>
                    <font color=red size=12>
                        {{mapobj.tile(zoom_x,zoom_y).get('/conditional/message', '') }}
                    </font>
                </center>
            </strong>
        {% endif %}    
                {% else %}
                    <div style="vertical-align: top; border: 1px solid; background-image:url(/icon/icons/blank.png;background-repeat:repeat;background-size:500px 500px; width:500; height:500; display:table-cell">
                {% endif %}
                    {% for icontuple in mapobj.tile_icons(zoom_x,zoom_y) %}
                        {% set k = icontuple[0] %}
                        {% set v = icontuple[1] %}
                        {% set section = icontuple[2] %}
                        <img title="{{k}}" src="/icon/{{v}}" width=100 onclick="itemclickHandler({{zoom_x}},{{zoom_y}}, '{{section}}', '{{k}}')">
                    {% endfor %}
                    {% if charicons %}
                    {% for idx in charicons[(zoom_x, zoom_y)] %}
                        {% set char = campaign.characterlist[idx] %}
                        {% if char %}
                            {% set title = char.displayname() %}
                            {% set index = idx %}
                            {% set icon = char.get('/core/icon', '') %}
                            <img title="{{title}}" src="/icon/{{icon}}" width=100 onclick="charclickHandler({{zoom_x}},{{zoom_y}}, '{{index}}')">
                        {% endif %}
                    {% endfor %}
                    {% endif %}
                </div>
            </div> 
        </div> 
                <div style="vertical-align: top; border: 3px solid; background-color:#ccffcc; display: table-cell;">
                    <form method=post>
                        <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                        <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                    {% if editmode %}
                        <strong>Tile Editor</strong><br>
                            <select name="load_tile_from_file">
                                {% for tile in tilelist |sort %}
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
                                {% for item in itemlist|sort %}
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
                        <strong>Tile actions</strong><br>
                       {% if mapobj.tile(zoom_x,zoom_y).canenter() %}
                            <input type=submit name="movehere" value="Move Here">
                            <br>
                            <input type=submit name="moveallhere" value="Party Move Here">
                            <br>
                            {% if mapobj.tile_icons(zoom_x,zoom_y) and not mapobj.tile(zoom_x, zoom_y).tiletype() == 'shop' %}
                                <input type=submit name="pickupall" value="Pick up all">
                                <br>
                            {% endif %}
                       {% endif %}
                       {% if mapobj.tile(zoom_x,zoom_y).tiletype() == 'link' %}
                            <input type=submit name="followlink" value="Go to next map"><br>
                       {% endif %}
                       {% if mapobj.tile(zoom_x, zoom_y).tiletype() == 'shop' %}
                       {% endif %}
                    {% endif %}
                    </form>
            {% if editmode %}
                <div style="vertical-align: top; background-color: #ccffcc; display: table-cell;">
                <script language="javascript" type="text/javascript" src="/js?path=editarea_0_8_2/edit_area/edit_area_full.js">
                </script>
                        <strong>Python Console:</strong>Current map object: map<form method=post>
                            <textarea id="pythonconsole" cols=100 rows=30 name="pythonconsole"></textarea><br>
                            <script language="javascript" type="text/javascript">
                                editAreaLoader.init({
                                    id : "pythonconsole"       // textarea id
                                    ,syntax: "python"           // syntax to be uses for highgliting
                                    ,start_highlight: true      // to display with highlight mode on start-up
                                });
                            </script>
                            <input type=submit value="Run code">
                        </form><br>
                        <strong>Raw JSON:</strong><form method=post>
                            <input type=hidden name="clicked_x" id="clicked_x" value="{{zoom_x}}">
                            <input type=hidden name="clicked_y" id="clicked_y" value="{{zoom_y}}">
                            <textarea id="jsonbox" cols=100 rows=30 name="jsonbox">{{mapobj.tile(zoom_x,zoom_y)}}</textarea><br>
                            <script language="javascript" type="text/javascript">
                                editAreaLoader.init({
                                    id : "jsonbox"       // textarea id
                                    ,syntax: "python"           // syntax to be uses for highgliting
                                    ,start_highlight: true      // to display with highlight mode on start-up
                                });
                            </script>
                            <input type=submit value="Update tile JSON" name="updatejson">
                        </form>
                    </div>
                </div>
            {% else %}
                {% if detailview %}
                <div id="detailview" class="detail" style="vertical-align: top; background-color: #ccffcc; display: table-cell;">
                     <div  style="display: table-cell; background-color: #aaffcc; border: 2px solid; padding: 5px;  border-radius: 25px; text-align: center; box-shadow: 5px 5px 2px #888888; " onclick="document.getElementById('detailview').style.display='none';document.getElementById('fade').style.display='none'">Close</div>
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

                                    {% for option in attackmods|sort %}
                                        <div>
                                            <input type=checkbox name=attackmods value="{{option}}">
                                            <label>{{option}}</label>
                                        </div>
                                    {% endfor %}
                                    <div>
                                        <input type=text name="custom_tohit" size=2 value="0">
                                        <lable>Custom to-hit modifier</lable>
                                    </div>                                
                                    <input type=submit name="attack" value="Calculate attack roll">
                                </fieldset>
                                <fieldset>
                                    <legend>Combat results</legend>
                                    <div>
                                        <input type=text name="damage_amt" size=2 value="0">
                                        <lable>Take Damage</lable>
                                    </div>                                
                                    <div>
                                        <input type=text name="heal_amt" size=2 value="0">
                                        <lable>Heal for</lable>
                                    </div>             
                                      <input type=submit name="combatresult" value="Apply combat result">   
                                </fieldset>               
                                <fieldset>
                                    <label>Tactical Items</lable>
                                    <select name="tact_item">
                                     {% for item in current_char.inventory_generator(sections=['pack']) %}
                                        {% if item[1].itemtype() != 'spell' and item[1].itemtype() != 'weapon'
                                         and item[1].itemtype() != 'armor' and item[1].get('/core/charges', 0) != 0 %}
                                            <option value="{{item[2]}}">{{item[1].displayname()}}
                                        {% endif %}
                                     {% endfor %}   
                                     <select>
                                    <input type=submit name="useitem" value="Use item">
                                </fieldset>
                                <fieldset>
                                    <label>Tactical Spells</lable>
                                    <select name="tact_spell">
                                     {% for idx, spell in tactical_spells %}
                                        <option value="{{idx}}">{{spell.displayname()}}
                                     {% endfor %}   
                                     <select>
                                    <input type=submit name="castspell" value="Cast Spell">
                                </fieldset>

                            {% endif %}
                        <fieldset>
                            <legend>Details</legend>
                            {% if detailicon %}
                            <img src=/icon/{{detailicon}} align=right>
                            {% endif %}
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
                    </fieldset>
                    <div  style="display: table-cell; background-color: #aaffcc; border: 2px solid; padding: 5px;  border-radius: 25px; text-align: center; box-shadow: 5px 5px 2px #888888; " onclick="document.getElementById('detailview').style.display='none';document.getElementById('fade').style.display='none'">Close</div>
                    </div>
                    <div id="fade" class="black_overlay"></div>
                    {% endif %}
                {%endif%}
            </div>
        </div>
</div>
