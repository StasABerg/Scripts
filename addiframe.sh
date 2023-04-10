#!/bin/bash

input_file="domain.txt"

if [[ -f $input_file ]]; then
    while IFS=' ' read -r domain brand_name; do
        case $brand_name in
            brand1) url='https://domain1/slug1/?';;
            brand2) url='https://domain2/slug2/?';;
            brand3) url='https://domain3/slug3/?';;
            *)
                echo "Invalid brand name. Skipping."
                continue
                ;;
        esac

url="${url}${domain}"
unique_identifier='iframeurl'
js_files=("/path/to/${domain}/json/file/"*.js)

if [ ${#js_files[@]} -eq 1 ]; then
    if grep -q "$unique_identifier" "${js_files[0]}"; then
        echo "Existing template found in ${js_files[0]}. Skipping."
    else
        template=$(cat <<EOT

var meta = document.createElement('meta');
meta.name = "viewport";
meta.content = "width=device-width, initial-scale=1, maximum-scale=1";
document.getElementsByTagName('head')[0].appendChild(meta);
var iframeurl = '${url}';
var iframewidth = 1584;
var iframeheight = 2176;
document.write('<div style="width:' + iframewidth + 'px; margin:0 auto;">');
document.write('<iframe src="' + iframeurl + '" width="' + iframewidth + '" height="' + iframeheight + '" frameborder="no" border="0" marginwidth="0" marginheight="0"scrolling="no"></iframe>');
document.write('</div>');
document.write('<style type="text/css">');
document.write(' ADD_HERE_MANUALLY_HTML_ELEMENTS_TO_REMOVE{');
document.write(' background-color:white;');
document.write(' visibility:hidden;');
document.write(' display:none;');
document.write(' position:absolute;');
document.write(' left:0px;');
document.write(' top:0px;');
document.write('}');
document.write(' html, div, body, iframe {');
document.write(' width: 100% !important;');
document.write(' min-width: 100% !important;');
document.write('}');
document.write('</style>');
EOT
)
        echo -e "\n${template}" >> "${js_files[0]}"
        echo "JavaScript content has been appended to ${js_files[0]}"
    fi
else
    echo "Error: Either no .js file found or multiple .js files found in the directory."
    exit 1
fi
done < "$input_file"
else
    echo "Error: domain.txt file not found."
    exit 1
fi
