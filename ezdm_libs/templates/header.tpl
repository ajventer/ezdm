<html>
<head>
    <title>{{title}}</title>
</head>
<body>
<center>
    <div style="background-color: #ADADFF; border: 3px solid;">
        <div style="display: table-row; border: 1px solid;; background-color: #ADADFF; ">
            <div style="display: table-cell; border: 1px solid; ">
                <input type=button value="Campaign" onclick="window.location = '/mode/campaign'">
                <input type=button value="Unload" onclick="window.location = '/switch_campaign'">
            </div>
            <div style="display: table-cell; border: 1px solid;">
            <td bgcolor=lightblue width=50%><center><strong>{{title}}</strong></center>
            {% if character %}   
                </div><div style="display: table-cell; border: 1px solid;">
                Current character:
                    <img src="/icon/{{character.get('/core/icon','')}}" height=25>{{character.displayname()}}
                    <input type=button value="End Round" onclick="window.location = '/endround'">
            {% endif %}
            </div>
            <div style="display: table-cell; border: 1px solid;">
                <input type=button value="Dungeon Master" onclick="window.location = '/mode/dm'">
            </div>
        </div>
    </div>
