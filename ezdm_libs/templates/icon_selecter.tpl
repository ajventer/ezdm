<strong>Icon Selector:</strong><br>
Click an image to automatically set the icon field to it.<br>
<table border=1 bordercolor=blue>
{% for icon in icons %}
<tr><td>
{% if selected == icon %}
	Current:<br>
{% endif %}
	<img align=left height=50 src=/icon/{{icon}} onclick="document.getElementById('core/icon').value = '{{icon}}';" >
    </td><td valign=middle><input type=button onclick="document.getElementById('core/icon').value = '{{icon}}';" value={{icon}}>
</td></tr>
{% endfor %}

</table>