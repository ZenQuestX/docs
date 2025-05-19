CSVにエクスポートする複数のシートがあり、各シートの列数が異なるケースでの対応ですね。シートの最終列と最終行を特定する関数を作成するのが最適な解決策だと思います。

以下にVBAでシートごとに最終列と最終行を求める関数を作成しました：

```vba
Function GetSheetLastRowCol(ws As Worksheet) As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim result(1 To 2) As Long
    
    ' 使用されている最終行を取得
    lastRow = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByRows, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Row
    
    ' 使用されている最終列を取得
    lastCol = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByColumns, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Column
    
    result(1) = lastRow
    result(2) = lastCol
    
    GetSheetLastRowCol = result
End Function
```

この関数を使って、各シートをCSVファイルとして出力するコードの例は以下のようになります：

```vba
Sub ExportAllSheetsToCSV()
    Dim ws As Worksheet
    Dim lastRowCol As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim filePath As String
    Dim i As Long, j As Long
    Dim data As String
    Dim fileNum As Integer
    
    ' 各シートに対して処理を実行
    For Each ws In ThisWorkbook.Worksheets
        ' 最終行と最終列を取得
        lastRowCol = GetSheetLastRowCol(ws)
        lastRow = lastRowCol(1)
        lastCol = lastRowCol(2)
        
        ' 出力ファイルパスを設定
        filePath = ThisWorkbook.Path & "\" & ws.Name & ".csv"
        fileNum = FreeFile
        
        ' CSVファイルを作成
        Open filePath For Output As #fileNum
        
        ' データを行ごとに処理
        For i = 1 To lastRow
            data = ""
            ' 列ごとに処理
            For j = 1 To lastCol
                ' セルの値を取得してCSV形式に追加
                If j > 1 Then data = data & ","
                
                ' セルの値をCSV形式にフォーマット
                If Not IsEmpty(ws.Cells(i, j).Value) Then
                    ' 文字列の場合、ダブルクォートで囲む
                    If IsNumeric(ws.Cells(i, j).Value) Then
                        data = data & ws.Cells(i, j).Value
                    Else
                        ' カンマやダブルクォートを含む場合の処理
                        Dim cellValue As String
                        cellValue = ws.Cells(i, j).Value
                        ' ダブルクォートをエスケープ（"" に置換）
                        cellValue = Replace(cellValue, """", """""")
                        data = data & """" & cellValue & """"
                    End If
                End If
            Next j
            
            ' 行データをファイルに書き込み
            Print #fileNum, data
        Next i
        
        ' ファイルを閉じる
        Close #fileNum
        
        Debug.Print ws.Name & " をCSVファイルにエクスポートしました: " & filePath
    Next ws
    
    MsgBox "すべてのシートがCSVファイルにエクスポートされました。", vbInformation
End Sub
```

この実装によって、各シートの実際のデータ範囲に基づいて最終行と最終列を正確に特定し、それに応じてCSVファイルを出力できます。各シートは個別のCSVファイルとして保存されます。

何か特定の要件や質問があれば、お聞かせください。

はい、特定のシート名だけをCSVに出力する場合は、シート名のリストを作成してそれをループする方法が適切です。以下に、その実装例を示します：

```vba
Sub ExportSpecificSheetsToCSV()
    Dim ws As Worksheet
    Dim lastRowCol As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim filePath As String
    Dim i As Long, j As Long
    Dim data As String
    Dim fileNum As Integer
    Dim sheetNames As Variant
    Dim sheetName As Variant
    Dim sheetExists As Boolean
    
    ' エクスポートするシート名のリストを定義
    sheetNames = Array("Sheet1", "売上データ", "集計表", "マスタ")
    
    ' 各シート名に対して処理を実行
    For Each sheetName In sheetNames
        sheetExists = False
        
        ' シートが存在するか確認
        For Each ws In ThisWorkbook.Worksheets
            If ws.Name = sheetName Then
                sheetExists = True
                Exit For
            End If
        Next ws
        
        ' シートが存在する場合のみ処理を続行
        If sheetExists Then
            ' 最終行と最終列を取得
            lastRowCol = GetSheetLastRowCol(ws)
            lastRow = lastRowCol(1)
            lastCol = lastRowCol(2)
            
            ' 出力ファイルパスを設定
            filePath = ThisWorkbook.Path & "\" & ws.Name & ".csv"
            fileNum = FreeFile
            
            ' CSVファイルを作成
            Open filePath For Output As #fileNum
            
            ' データを行ごとに処理
            For i = 1 To lastRow
                data = ""
                ' 列ごとに処理
                For j = 1 To lastCol
                    ' セルの値を取得してCSV形式に追加
                    If j > 1 Then data = data & ","
                    
                    ' セルの値をCSV形式にフォーマット
                    If Not IsEmpty(ws.Cells(i, j).Value) Then
                        ' 文字列の場合、ダブルクォートで囲む
                        If IsNumeric(ws.Cells(i, j).Value) Then
                            data = data & ws.Cells(i, j).Value
                        Else
                            ' カンマやダブルクォートを含む場合の処理
                            Dim cellValue As String
                            cellValue = ws.Cells(i, j).Value
                            ' ダブルクォートをエスケープ（"" に置換）
                            cellValue = Replace(cellValue, """", """""")
                            data = data & """" & cellValue & """"
                        End If
                    End If
                Next j
                
                ' 行データをファイルに書き込み
                Print #fileNum, data
            Next i
            
            ' ファイルを閉じる
            Close #fileNum
            
            Debug.Print ws.Name & " をCSVファイルにエクスポートしました: " & filePath
        Else
            Debug.Print "シート '" & sheetName & "' が見つかりません。"
        End If
    Next sheetName
    
    MsgBox "指定されたシートがCSVファイルにエクスポートされました。", vbInformation
End Sub

Function GetSheetLastRowCol(ws As Worksheet) As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim result(1 To 2) As Long
    
    On Error Resume Next
    ' 使用されている最終行を取得
    lastRow = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByRows, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Row
    
    ' 使用されている最終列を取得
    lastCol = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByColumns, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Column
    
    On Error GoTo 0
    
    ' データが見つからない場合は1行1列を返す
    If lastRow = 0 Then lastRow = 1
    If lastCol = 0 Then lastCol = 1
    
    result(1) = lastRow
    result(2) = lastCol
    
    GetSheetLastRowCol = result
End Function
```

このコードには以下の特徴があります：

1. `sheetNames` 配列に出力したいシート名をリストとして定義しています。必要に応じてシート名を変更できます。

2. リスト内の各シート名について、そのシートがワークブック内に存在するかを確認し、存在する場合のみCSV出力を行います。

3. 存在しないシート名についてはデバッグ出力でメッセージを表示します。

4. `GetSheetLastRowCol` 関数にエラーハンドリングを追加して、データが見つからない場合でも安全に動作するようにしています。

この方法であれば、出力したい特定のシートだけを効率的にCSVファイルに変換できます。必要に応じて、シート名のリストを別の場所（例えば特定のシートのセル範囲など）から読み込むように変更することも可能です。

はい、シート名とファイル名のマッピングを定数として定義し、一度にコレクションに追加することができます。以下に、その実装例を示します：

```vba
Sub ExportSpecificSheetsToCSV()
    Dim ws As Worksheet
    Dim lastRowCol As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim filePath As String
    Dim i As Long, j As Long
    Dim data As String
    Dim fileNum As Integer
    Dim sheetDict As Object
    Dim sheetName As Variant
    Dim fileName As String
    
    ' シート名とファイル名のマッピングを定数で定義
    Const SHEET_FILE_MAPPINGS As String = "Sheet1,営業データ_2023|売上データ,売上集計_全店舗|集計表,月次報告_本社提出用|マスタ,顧客マスタ_最新"
    
    ' Dictionary オブジェクトを作成 (キー: シート名, 値: ファイル名)
    Set sheetDict = CreateObject("Scripting.Dictionary")
    
    ' 定数からマッピングを解析してDictionaryに追加
    Dim mappings As Variant
    Dim mapping As Variant
    Dim pair As Variant
    
    mappings = Split(SHEET_FILE_MAPPINGS, "|")
    For Each mapping In mappings
        pair = Split(mapping, ",")
        If UBound(pair) = 1 Then ' 正しく分割されていることを確認
            sheetDict.Add pair(0), pair(1)
        End If
    Next mapping
    
    ' 各シート名に対して処理を実行
    For Each sheetName In sheetDict.Keys
        On Error Resume Next
        Set ws = ThisWorkbook.Worksheets(sheetName)
        On Error GoTo 0
        
        ' シートが存在する場合のみ処理を続行
        If Not ws Is Nothing Then
            ' 最終行と最終列を取得
            lastRowCol = GetSheetLastRowCol(ws)
            lastRow = lastRowCol(1)
            lastCol = lastRowCol(2)
            
            ' 出力ファイルパスを設定（Dictionaryの値をファイル名として使用）
            fileName = sheetDict(sheetName)
            filePath = ThisWorkbook.Path & "\" & fileName & ".csv"
            fileNum = FreeFile
            
            ' CSVファイルを作成
            Open filePath For Output As #fileNum
            
            ' ヘッダー行（1行目）を書き込み
            data = ""
            For j = 1 To lastCol
                If j > 1 Then data = data & ","
                
                If Not IsEmpty(ws.Cells(1, j).Value) Then
                    If IsNumeric(ws.Cells(1, j).Value) Then
                        data = data & ws.Cells(1, j).Value
                    Else
                        Dim headerValue As String
                        headerValue = ws.Cells(1, j).Value
                        headerValue = Replace(headerValue, """", """""")
                        data = data & """" & headerValue & """"
                    End If
                End If
            Next j
            Print #fileNum, data
            
            ' データ行（3行目から最終行まで）を書き込み
            For i = 3 To lastRow ' 2行目をスキップして3行目から開始
                data = ""
                For j = 1 To lastCol
                    If j > 1 Then data = data & ","
                    
                    If Not IsEmpty(ws.Cells(i, j).Value) Then
                        If IsNumeric(ws.Cells(i, j).Value) Then
                            data = data & ws.Cells(i, j).Value
                        Else
                            Dim cellValue As String
                            cellValue = ws.Cells(i, j).Value
                            cellValue = Replace(cellValue, """", """""")
                            data = data & """" & cellValue & """"
                        End If
                    End If
                Next j
                Print #fileNum, data
            Next i
            
            ' ファイルを閉じる
            Close #fileNum
            
            Debug.Print sheetName & " をCSVファイルにエクスポートしました: " & filePath
        Else
            Debug.Print "シート '" & sheetName & "' が見つかりません。"
        End If
        
        ' 次のループのためにワークシート変数をクリア
        Set ws = Nothing
    Next sheetName
    
    MsgBox "指定されたシートがCSVファイルにエクスポートされました。", vbInformation
End Sub

Function GetSheetLastRowCol(ws As Worksheet) As Variant
    Dim lastRow As Long
    Dim lastCol As Long
    Dim result(1 To 2) As Long
    
    On Error Resume Next
    ' 使用されている最終行を取得
    lastRow = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByRows, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Row
    
    ' 使用されている最終列を取得
    lastCol = ws.Cells.Find(What:="*", _
                After:=ws.Range("A1"), _
                LookIn:=xlFormulas, _
                LookAt:=xlPart, _
                SearchOrder:=xlByColumns, _
                SearchDirection:=xlPrevious, _
                MatchCase:=False).Column
    
    On Error GoTo 0
    
    ' データが見つからない場合は1行1列を返す
    If lastRow = 0 Then lastRow = 1
    If lastCol = 0 Then lastCol = 1
    
    result(1) = lastRow
    result(2) = lastCol
    
    GetSheetLastRowCol = result
End Function
```

このコードでは以下の変更を行いました：

1. マッピング情報を一つの文字列定数 `SHEET_FILE_MAPPINGS` として定義しています。
   ```vba
   Const SHEET_FILE_MAPPINGS As String = "Sheet1,営業データ_2023|売上データ,売上集計_全店舗|集計表,月次報告_本社提出用|マスタ,顧客マスタ_最新"
   ```

2. この定数を解析して Dictionary に追加する処理を実装しています。
   ```vba
   mappings = Split(SHEET_FILE_MAPPINGS, "|")
   For Each mapping In mappings
       pair = Split(mapping, ",")
       If UBound(pair) = 1 Then
           sheetDict.Add pair(0), pair(1)
       End If
   Next mapping
   ```

この方法を使えば、マッピング情報はすべて1つの定数として管理でき、コードの見通しがよくなります。マッピング情報を変更したい場合は、`SHEET_FILE_MAPPINGS` 定数の値を変更するだけで済みます。

別の方法として、マッピングを2次元配列として定義する方法もあります：

```vba
' 2次元配列でマッピングを定義
Dim mappingArray As Variant
mappingArray = Array( _
    Array("Sheet1", "営業データ_2023"), _
    Array("売上データ", "売上集計_全店舗"), _
    Array("集計表", "月次報告_本社提出用"), _
    Array("マスタ", "顧客マスタ_最新") _
)

' Dictionary に追加
For i = LBound(mappingArray) To UBound(mappingArray)
    sheetDict.Add mappingArray(i)(0), mappingArray(i)(1)
Next i
```

こちらの方法も検討されてみてはいかがでしょうか。
