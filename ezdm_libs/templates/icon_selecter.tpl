</div>
<div style="display: table-cell">
<strong>Icon Selector:</strong><br>
Click an image to automatically set the icon field to it.<br>
{% for icon in icons|sort %}
{% if selected == icon %}
	<div style="box-shadow: 5px 5px 2px #888888; background-color: #aaffcc;  border: 1px solid" onclick="document.getElementById('core/icon').value = '{{icon}}';">
{% else %}
    <div style="box-shadow: 5px 5px 2px #888888; background-color: #ccffcc; border: 1px solid" onclick="document.getElementById('core/icon').value = '{{icon}}';">
{% endif %}
	<img height=50 src=/icon/{{icon}} >
    {{icon}}
</div>
{% endfor %}
</div>
</div>