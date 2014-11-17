<html>
<head>
    <title>{{title}}</title>
       <title>LIGHTBOX EXAMPLE</title>
        <style>
        .black_overlay{
            display: block;
            position: absolute;
            top: 0%;
            left: 0%;
            width: 100%;
            height: 100%;
            background-color: black;
            z-index:1001;
            -moz-opacity: 0.8;
            opacity:.80;
            filter: alpha(opacity=80);
        }
        .white_content {
            display: block;
            position: absolute;
            top: 25%;
            left: 25%;
            width: 50%;
            height: 50%;
            padding: 16px;
            border: 16px solid orange;
            background-color: white;
            z-index:1002;
            overflow: auto;
            border-color: #ADADFF;
        }
        .detail {
            display: block;
            position: absolute;
            top: 5%;
            left: 30%;
            width: 30%;
            height: 85%;
            padding: 16px;
            border: 16px solid orange;
            background-color: white;
            z-index:1002;
            overflow: auto;
            border-color: #ADADFF;
        }        
    </style>    
</head>
<body>
    <div style="background-color: #ADADFF; border: 3px solid;">
        {% if messages %}
            <div id="light" class="white_content">
                <div align="right">

                <div  style="display: table-cell; background-color: #aaffcc; border: 2px solid; padding: 5px;  border-radius: 25px; text-align: center; box-shadow: 5px 5px 2px #888888; " onclick="document.getElementById('light').style.display='none';document.getElementById('fade').style.display='none'">Close</div>

                </div>
                <div>
                    {% for message in messages.messages %}
                        {{message}}<br>
                    {% endfor %}
                    {% for message in messages.warnings %}
                        <font color=orange>{{message}}</font><br>
                    {% endfor %}
                    {% for message in messages.errors %}
                        <font color=red>{{message}}</font><br>
                    {% endfor %}
                </div>
                {% if character and character.is_casting %}
                    <strong>{{character.displayname()}} is casting a spell</strong><br>
                    {% if characters %}
                        <form method=post action="/newchar">
                        <select name="newchar">
                        {% for character in characters %}
                            <option value="{{characters.index(character)}}">{{character.name()}} ({{characters.index(character)}})</option>
                        {% endfor %}
                        </select>
                        <input type=submit value="End round and continue casting">
                        </form>
                    {% endif %}                        
                        <a href="/interrupt">Stop casting and do something else</a>
                {% endif %}

             </div>
            <div id="fade" class="black_overlay"></div>
        {% endif %}    
<center>        
        <div style="display: table-row; border: 1px solid;; background-color: #ADADFF; ">
            <div style="display: table-cell; border: 1px solid; ">
                <input type=button value="Campaign" onclick="window.location = '/mode/campaign'">
                <input type=button value="Unload" onclick="window.location = '/switch_campaign'">
            </div>
            <div style="display: table-cell; border: 1px solid;">
            <center><strong>{{title}}</strong></center>
            {% if character %}   
                </div><div style="display: table-cell; border: 1px solid;">
                Current character:
                    <img src="/icon/{{character.get('/core/icon','')}}" height=25>{{character.displayname()}}
            {% endif %}
            </div>
            <div style="display: table-cell; border: 1px solid;">
            {% if characters %}
                <form method=post action="/newchar">
                <select name="newchar">
                {% for character in characters %}
                    <option value="{{characters.index(character)}}">{{character.name()}} ({{characters.index(character)}})</option>
                {% endfor %}
                </select>
                <input type=submit value="Switch Character">
                </form>
            {% endif %}
            </div>
            <div style="display: table-cell; border: 1px solid;">
                <input type=button value="Dungeon Master" onclick="window.location = '/mode/dm'">
            </div>
        </div>
    </div>
<center>

