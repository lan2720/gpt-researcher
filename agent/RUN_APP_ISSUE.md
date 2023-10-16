# 启动应用
```
uvicorn main:app --reload
```
# OSError: cannot load library 'gobject-2.0-0'
- github有相关[issue](https://github.com/Kozea/WeasyPrint/issues/1556)
- 解决办法:
    ```
    sudo  ln -s  /opt/homebrew/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0

    sudo ln -s /opt/homebrew/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0

    sudo ln -s /opt/homebrew/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz

    sudo ln -s /opt/homebrew/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1

    sudo ln -s /opt/homebrew/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0
    ```