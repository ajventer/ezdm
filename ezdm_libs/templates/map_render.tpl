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

<table border=1>
    <tr>
        <td colspan=20 bgcolor=lightblue>
            <center><strong>{{name}}
                {% if turn %} - {{turn}}'s turn{% endif %}
            </strong></center>
        </td>
    </tr>

    {% for row in tiles%}
        {% set x = loop.index - 1 %}
        <tr>
            {% for col in row %}
                {% set y = loop.index - 1%}
                {% if col.core and col.core.icon %}
                <td valign=bottom style="background-image:url(/icon/{{col.core.icon}});background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                {% else %}
                <td valign=bottom style="background-image:url(/icon/blank.png);background-repeat:no-repeat;background-size:50px 50px; width:50; height:50" >
                {% endif %}
                    <input type=button onclick="clickHandler({{x}},{{y}})" value="->">
                </td>
            {% endfor %}
        </tr>
    {% endfor %}