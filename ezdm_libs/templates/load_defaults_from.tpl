<center>
<form action="{{action}}" method=post>
<table border=1>
    <tr>
        <td bgcolor=lightgray colspan=2>
            <center>{{name}}s</center>
        </td>
    </tr>
    <td>
        Load default values from
    </td>
    <td>
        <select name="{{keyname}}">
            {%for item in items %}
                <option value="{{item}}">{{item}}</option>
            {%endfor%}
        </select>
    </td>
</tr>
    <td colspan=2>
        <center><input type=submit value="Continue"></center>
    </td>
</tr>
</table>
</form>
</center>