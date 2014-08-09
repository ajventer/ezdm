<form method='post'>
<table border=1>
    <tr>
        <td bgcolor=lightgray>
            <center>{{name}}s</center>
        </td>
    </tr>
    <td>
        <select name="{{keyname}}">
            {% if allow_new %}
                <option value="New {{name}}">New {{name}}</option>
            {% endif %}
            {%for item in items|sort %}
                <option value="{{item}}">{{item}}</option>
            {%endfor%}
        </select>
    </td>
</tr>
{% if allow_raw %}
    <tr>
        <td>
            <input type=checkbox name="raw_mode" value="raw">Edit JSON in raw mode
        </td>
    </tr>
{% endif %}
<tr>
    <td colspan=2>
        <center><input type=submit name="LoadDefaultFrom" value="Continue"></center>
    </td>
</tr>
</table>
</form>
