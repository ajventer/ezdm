<form action="{{action}}" method=post>
<table border=1 width=100%>
    <tr>
        <td bgcolor=lightgray colspan=2>
            <center>{{name}}s</center>
        </td>
    </tr>
    <td>
        Load default values for {{name}} from
    </td>
    <td>
        <select name="{{keyname}}">
            {%for item in items %}
                <option value="{{item}}">{{item}}</option>
            {%endfor%}
        </select>
    </td>
</tr>
<td>
    <td>
        <input type=submit value="Continue">
    </td>
</tr>
</table>
</form>