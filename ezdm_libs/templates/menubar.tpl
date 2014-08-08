
    <div style="display: table-row; border-spacing: 40px; ">
         {%for key in menuitems |sort %}
            <div onclick="window.location = '/action/{{key}}'" style="background-color: #aaffcc; border: 2px solid; display: table-cell; padding: 5px;  border-radius: 25px; text-align: center; box-shadow: 5px 5px 2px #888888; ">
                {{menuitems[key]}}
            </div>
            <div style="display: table-cell; padding: 5px;">
            </div>
        {%endfor%}
    </div>



