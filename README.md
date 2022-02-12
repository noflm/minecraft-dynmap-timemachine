# Minecraft Dynmap Time Machine

MinecraftのSpigotプラグイン、Dynmapが生成するWebマップからワールドの画像を直接一括でダウンロードし、非常に高い解像度で1枚の画像に合成するコマンドラインツールです。
Python3.6以上で動作します。


**※このツールの仕様上、非同期処理を用いて短時間に数万枚の画像をダウンロードするようになっています。**
**言い方を変えれば短時間に数万回のリクエスト(1秒間に200以上のリクエスト)をダウンロード先のWebサーバーにする事になります。**
**この行為はWebサーバーに非常に大きな負荷をかける行為です。**
**絶対に自分が管理する(許可された)Dynmap以外でこのツールを使用しないで下さい。**
**最悪の場合"電子計算機損壊等業務妨害罪"等の罪に問われる可能性があります。**
**このツールを使用した事により発生した問題や故障に関して、ツール制作者は一切の責任を負いかねます。**
**自己責任かつご自分の管理下にあるDynmapのバックアップ等にご活用ください。**


![Scaled down image](https://raw.githubusercontent.com/noflm/minecraft-dynmap-timemachine/master/sample_imgs/life_81x54_s_comp.jpg)


コマンドパラメータ:

    $ python3 dynmap-timemachine.py -h
    usage: dynmap-timemachine.py [-h] [--list-worlds] [--list-maps] [-t [THRESHOLD]] [-q] [-v]
                   base_url [world] [map] [center] [boundary_size] [zoom] [dest]
    
    positional arguments:
      base_url              Dynamp server URL
      world                 world name, use --list-worlds to list available worlds
      map                   map name, use --list-maps to list available maps
      center                minecraft cooridnates, use format: [x,y,z]
      boundary_size         size in tiles, use format: [h,v]
      zoom                  zoom level, 0 = maximum zoom
      dest                  output file name or directory
    
    optional arguments:
      -h, --help            show this help message and exit
      --list-worlds         list available worlds from this Dynmap server and exit
      --list-maps           list available maps for this world and exit
      -t [THRESHOLD], --threshold [THRESHOLD]
                            threshold for timelapse images
      -q, --quiet
      -v, --verbose

## インストール
このリポジトリをgitコマンドでクローンするかzipファイルでダウンロードして下さい。
その後ダウンロードしたファイルが有るディレクトリ内で以下のコマンドを実行します。
(venvの使用をお勧めします)

    $ python3 -m pip install -r requirements.txt

## 1. 1枚の高解像度マップ画像をダウンロード

試しに[えりぃとかふぇサーバー](https://nyahello.jp/docs/minecraft/elite_cafe/)の[Dynmap](https://maps.nyahello.jp/cafe/)、座標 `[748,64,-368]` から `20736x13824`px (286 Mpx image) の画像をダウンロードしてみましょう。


1. **ダウンロード先のDynmapに設定されているワールドの取得**

   ```
   $ python3 dynmap-timemachine.py --list-worlds https://maps.nyahello.jp/cafe/
   world - world
   world_the_end - world_the_end
   undertale - undertale
   RPG - RPG
   ```

   このサンプルではオーバーワールドのマップ画像を取得する為、マップ名`world`を使用します。

2. **ダウンロード先のDynmapに設定されているマップの種類の取得**

   ```
   $ python3 dynmap-timemachine.py --list-maps https://maps.nyahello.jp/cafe/ world
   flat - Flat
   surface - Surface
   cave - Cave
   ```
    
   このサンプルではSurfaceのマップ画像を取得する為、マップタイプ`surface`を使用します。
   
3. **ダウンロード先のワールド座標を設定しテスト画像をダウンロード**

   DynmapのWebマップ上で座標を確認するか、ゲーム内でF3を押し、画像ダウンロードを行いたい場所の座標を確認します。
   以下のコマンドを実行することでテスト画像をダウンロード出来ます。
   
   ```
   $ python3 dynmap-timemachine.py https://maps.nyahello.jp/cafe/ world surface \
       [748,64,-368] [3,2] 0 test.jpg
   ```
   
   Used parameters:
   
   - `https://maps.nyahello.jp/cafe/` - Dynmap's web map URL
   - `world` - World name
   - `surface` - Map type
   - `[748,64,-368]` - Minecraft coordiantes that will be automatically converted to tile names
   - `[3,2]` - Number of tiles I want to download in each direction from specified coordinates. That's two to the left and right, two to the top and bottom. This will actually download 6x4 grid where each tile is 128x128 pixels. In total this image will be 768x512 pixels
   - `0` - Zoom level. 0 means maximum zoom in. Number of zoom levels depend's on Dynamp's configuration
   - `test.jpg` - Output file name
   
   このコマンドを実行すると 768x512 px の画像がダウンロードされます。
   
   ![Preview from 6x4 grid](https://raw.githubusercontent.com/noflm/minecraft-dynmap-timemachine/master/sample_imgs/cafe_3x2_s.jpg)
   
4. **20736x13824pxの超高画質マップ画像をダウンロード (162x108 tiles)**
   
   最後に超高画質のマップ画像をダウンロードしてみましょう。
   
   ```
   $ python3 dynmap-timemachine.py -v https://maps.nyahello.jp/cafe/ world surface \
       [748,64,-368] [81,54] 0 full.jpg
   ```
   
   合計で「81 * 2 * 54 * 2 = 17496」タイルをダウンロードする必要があるので、サーバーの状況によっては時間がかかったり一部の画像がエラーで取得出来ない可能性があります。最終的な画像サイズは66.7MB(JPEGの場合)になります。(PNGだと593MB、TIFFだと820MB)
   
   ![The final image scaled down to 728px width](https://raw.githubusercontent.com/noflm/minecraft-dynmap-timemachine/master/sample_imgs/cafe_81x54_s_comp.jpg)
