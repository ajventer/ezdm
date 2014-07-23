<strong>Icon Selector:</strong><br>
Click an image to automatically set the icon field to it.<br>
{% for icon in icons %}
{% if selected == icon %}
	Current:<br>
{% endif %}
	<img height=50 src=/icon/{{icon}} onclick="document.getElementById('core/icon').value = '{{icon}}';" ><br>
{% endfor %}