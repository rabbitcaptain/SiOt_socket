"""SiOtの接続のためのクラス

     * ソースコードの一番始めに記載すること
     * importより前に記載する

Todo:
   TODOリストを記載
    * conf.pyの``sphinx.ext.todo`` を有効にしないと使用できない
    * conf.pyの``todo_include_todos = True``にしないと表示されない

"""

import socket
import math

class SiOt_TCP:
    """
    SiOtとのソケット通信のクライアントの保持と通信モジュール

    Attributes
    ----------
    client : socketクラス
        TCP通信のためのsocketクラス
    """
    def __init__(self, ip, port):
        """
        Parameters
        ----------
        ip : str
            SiOtのIPアドレス
        port : int
            SiOtのポート
        """
        print("SiOt接続開始･･･")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))
        print("接続完了!!")
        
    #16進数→2進数
    def htob(self, hexa: str) -> str:
        """
        16進数の文字列それぞれ2進数へ変換する
        ※ただし、見やすくするように桁の小さい方を左から並べる

        Parameters
        ----------
        hexa : str
            16進数の文字列
            例）3F2A

        Returns
        -------
        output : str
            2進数の文字列
            例）1100111101000101
        """
        size = len(hexa)
        output = ""

        for i in range(size):
            x = bin(int(hexa[i], 16))[2:].zfill(4)
            x_r = ''.join(list(reversed(x)))
            output = output + x_r
        return output
    
    #2進数→16進数
    def btoh(self, binary: str) -> str:
        """
        2進数の文字列それぞれ4つ区切りで16進数へ変換する
        ※ただし、見やすくするように2進数は桁の小さい方を左から並べる

        Parameters
        ----------
        hexa : str
            2進数の文字列
            例）1100111101000101

        Returns
        -------
        output : str
            16進数の文字列
            例）3F2A
        """
        size = len(binary) // 4
        output = ""

        for s in range(size):
            temp = binary[4 * s:4 * (s+1)]
            #文字列を逆転させる
            temp = ''.join(list(reversed(temp)))
            #１６進数の文字列に変換
            temp = hex(int(temp, 2))
            #大文字にする
            temp = temp[2].upper()
            output = output + temp
        return output
    
    def receive(self, msglen):
        """
        ソケット通信の送信結果を受信する

        Parameters
        ----------
        msglen : int
            受信メッセージの長さ

        Returns
        -------
        output : int
            受信メッセージ
        """
        output = ""
        #返信メッセージの長さが指定の長さまで受信
        while len(output) < msglen:
            response = self.client.recv(24).decode()
            output = output + response
            
        return output
        
        
    #IOチェック
    def IO_state_check(self):
        """
        SiOtのIO状態を確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            IO順序[IN1, IN2, IN3, IN4,・・・, OUT4, OUT3, OUT2, OUT1, OUT8, ・・・]
        """
        self.client.send(b"@R01CRLF")
        response = self.receive(14)[4:12]
        return self.htob(response)

    #FLAG状態チェック
    def FLAG_state_check(self):
        """
        SiOtのFLAG状態を確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            FLAG順序[FLAG1, FLAG2, FLAG3, FLAG4,・・・, FLAG45, FLAG46, FLAG47, FLAG48]
        """
        self.client.send(b"@R02CRLF")
        response = self.receive(18)[4:16]
        return self.htob(response)
    
    #Etherフラグのチェック
    def Ether_flag_check(self):
        """
        SiOtのEtherのフラグ状態を確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            EtherFLAG順序[Ether1, Ether2, Ether3, Ether4, Ether5, Ether6, Ether7, Ether8]
        """
        self.client.send(b"@R05CRLF")
        response = self.receive(8)[4:6]
        return self.htob(response)
    
    #稼働時間の確認
    def Time_check(self):
        """
        SiOtの稼働時間を確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            DAY(4桁)Hour(2桁)Min(2桁)Sec(2桁)
            全て16進数で表現されている
        """
        self.client.send(b"@R06CRLF")
        response = self.receive(16)[4:14]
        return response
    
    #OUTカウンタ値の確認
    def OutCounter_check(self):
        """
        SiOtのOUTカウンタを確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            OUT1～OUT16(各4桁)
        """
        self.client.send(b"@R07CRLF")
        response = self.receive(70)[4:68]
        return response
    
    #FLAGカウンタ値の確認
    def FlagCounter_check(self, flag_num):
        """
        SiOtのFLAGカウンタを確認する

        Parameters
        ----------
        flag_num : int
        フラグの番号

        Returns
        -------
        response : str
            n=0 FLAG1～16 各4桁
            n=1 FLAG17～32 各4桁
            n=2 FLAG33～48 各4桁
        """
        command = "@R09" + str(flag_num) + "CRLF"
        command = command.encode()
        self.client.send(command)
        response = self.receive(71)[4:69]
        return response
    
    #RUNの稼働状態
    def Run_check(self):
        """
        SiOtの稼働状態を確認する

        Parameters
        ----------

        Returns
        -------
        response : str
            1桁目:1=RUN 2=未使用 4=エラー 8:INIT
            2桁目:未使用
        """
        self.client.send(b"@R10CRLF")
        response = self.receive(8)[4:6]
        return response
    
    #Etherフラグの変更
    def EtherFlag_change(self, ether_flag):
        """
        SiOtのEtherフラグ変更を確認する

        Parameters
        ----------
        ether_flag : str
        2進数のEtherフラグ
        例）01000101

        Returns
        -------
        response : str
            @W02CRLFが返ってきたらOK
        """
        ether_flag = self.btoh(ether_flag)
        command = "@W02" + ether_flag + "CRLF"
        command = command.encode()
        self.client.send(command)
        response = self.receive(6)