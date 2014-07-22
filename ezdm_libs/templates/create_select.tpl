<form action="{{action}}" method=post>
<center>
<table border=1>
    <tr>
        <td bgcolor=lightgray colspan=2>
            <center>{{name}}s</center>
        </td>
    </tr>
    <td>
        Select {{name}}
    </td>
    <td>
        <select name="{{keyname}}">
            <option value="new_{{name}}">Create new {{name}}</option>
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