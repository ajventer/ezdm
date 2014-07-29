<form method='post'>
<table border=1>
    <tr>
        <td bgcolor=lightgray>
            <center>{{name}}s</center>
        </td>
    </tr>
    <td>
        <select name="{{keyname}}">
            {% if allow_new == 'True' %}
                <option value="New {{name}}">New {{name}}</option>
            {% endif %}
            {%for item in items|sort %}
                <option value="{{item}}">{{item}}</option>
            {%endfor%}
        </select>
    </td>
</tr>
    <td colspan=2>
        <center><input type=submit name="LoadDefaultFrom" value="Continue"></center>
    </td>
</tr>
</table>
</form>
