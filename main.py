import re #Regex: Veri Ayrıştırmak için kullandığım python kütüphanesi.
import subprocess #Powershell komutumu çalıştırmak için kullandığım libary.
from flask import Flask, render_template, session
from matplotlib.figure import Figure
from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import sys
from matplotlib.backends.backend_agg import FigureCanvasAgg

ziyaretciler = []
veriSayac=0
tarih=[]
adet=[]

uyariAdi=[]
adet4=[]

tarih2=[]
adet3=[]

uyari=[]
adet2=[]
bugununLogSayisi=""
dununLogSayisi=""
gunsayisi=0

#KULLANDIĞIM TÜM FONKSİYONLAR
def powerShellFonksiyon():
    # PowerShellden istediğim log düzeni ile loglarımı python projemin bulunduğu dizinde çalıştırılmasını sağladım.
    cmdKomut = "Get-WinEvent -LogName 'System' | Select-Object -Property TimeCreated, Id, LevelDisplayName, Message | Format-Table -AutoSize | Out-File -FilePath .\\Log.txt"
    # PowerShell komutumu çalıştırdım.
    subprocess.run(["powershell.exe", "-Command", cmdKomut])
def tarihAyristirma():
    tarih_deseni = r'\d{2}/\d{2}/\d{4}'  # regex ile tarihleri okumak için bu düzeni kullan dedim.
    # Tarihleri ve sayılarını saklayacak bir sözlük oluşturdum.
    tarih_sozlugu = {}
    # Dosyayı açtım ve içerikleri tek tek okudum ve tarih düzenime göre ayrıştırdım.
    with open("Log.txt", 'r', encoding="utf-16") as dosya:
        global veriSayac
        for satir in dosya:
            tarihler = re.findall(tarih_deseni, satir)
            for tarih in tarihler:
                if tarih in tarih_sozlugu:
                    tarih_sozlugu[tarih] += 1
                    veriSayac =veriSayac+1
                else:
                    tarih_sozlugu[tarih] = 1
                    veriSayac +=1

    with open("TarihAyristirlmis.txt", "w", encoding="utf-16") as dosya2:  # Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
        for tarih, sayi in tarih_sozlugu.items():
            dosya2.write(tarih + " " + str(sayi) + "\n")
            global gunsayisi
            gunsayisi=gunsayisi+1

    # Sonuçları ekrana yazdırın
    for tarih, sayi in tarih_sozlugu.items():
        print(f"{tarih}: {sayi} adet")

    # Dosyayı kapatın
    dosya.close()
def logAyristirma():
    logDeseni = r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})\s+(\d+)\s+(\w+)\s+(.+)"
    #regexin arayacağı log düzeni
    with open("Log.txt", "r", encoding="utf-16") as dosya:
        uyariTip = {}  # UYARI TİPLERİNİ HAFIZADA TUTACAK SÖZLÜK
        tumUyariTip={}
        critcalList = {}
        bilgi = ""
        uyari=""
        dikkat = ""
        seviye = ""
        for satir in dosya:
            match = re.match(logDeseni, satir)

            if match:
                tarih,saat, kod, seviye,veri =match.group(1), match.group(2), match.group(3),match.group(4),match.group(5)
                uyari=kod+" "+seviye
                dikkat=tarih+" "+seviye
                bilgi=seviye
            if seviye == "Critical":
                if dikkat in critcalList:
                    critcalList[dikkat] += 1
                else:
                    critcalList[dikkat] = 1
            if uyari in uyariTip:
                uyariTip[uyari] += 1
            else:
                uyariTip[uyari] = 1
            if bilgi in tumUyariTip:
                tumUyariTip[bilgi] += 1
            else:
                tumUyariTip[bilgi] = 1

        with open("UyariAyristirlmis.txt", "w", encoding="utf-16") as dosya2:#Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
            for uyari, sayi in uyariTip.items():
                dosya2.write(f'{uyari} {sayi} \n')
                print(f"{uyari}: {sayi} adet")

        with open("KritikAyristirlmis.txt", "w",encoding="utf-16") as dosya3:  # Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
            for dikkat, sayi in critcalList.items():
                dosya3.write(f'{dikkat} {sayi} \n')
                print(f"{dikkat}: {sayi} adet")


        with open("ToplamUyariAdetleri.txt", "w",encoding="utf-16") as dosya4:  # Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
            for uyari, sayi in tumUyariTip.items():
                dosya4.write(f'{uyari} {sayi} \n')
                print(f"{uyari}: {sayi} adet")

#Tüm Log Zaman Grafiği.
def cizgiGrafik():
    # Matplotlib grafiği oluşturun
    fig = Figure(figsize=(6, 4), dpi=100)
    grafik = fig.add_subplot(111)
    grafik.plot(list(reversed(tarih)), list(reversed(adet)), label='_nolegend_',color='blue')  # Çizgi grafiğinin rengini değiştirme...
    grafik.set_xlabel("Tarih")  # set_xlabel kullanılmalı
    grafik.set_ylabel("SİSTEM LOGLANMA SAYISI")  # set_ylabel kullanılmalı
    grafik.set_title("Sistem Log Meşguliyet Grafiği")  # set_title kullanılmalı
    grafik.set_xticks([tarih[0], tarih[-1]])
    kaydetme_yolu = "static/images/grafik.png"
    # Grafiği images olarak kaydetme...
    fig.savefig(kaydetme_yolu) ##

#Log Kritik Grafiği .
def cizgiGrafik2():
    # Matplotlib grafiği oluşturun
    fig = Figure(figsize=(6, 4), dpi=100)
    grafik = fig.add_subplot(111)
    grafik.plot(list(reversed(tarih)), list(reversed(adet)), label='_nolegend_',color='lightblue')  # Çizgi grafiğinin rengini değiştirme...
    grafik.plot(list(reversed(tarih2)), list(reversed(adet3)), label='_nolegend_',color='red')  # Çizgi grafiğinin rengini değiştirme...
    grafik.set_xlabel("Tarih")  # set_xlabel kullanılmalı
    grafik.set_ylabel("SİSTEM LOGLANMA SAYISI")  # set_ylabel kullanılmalı
    grafik.set_title("Sistem Log/Kritik Grafiği")  # set_title kullanılmalı
    grafik.set_xticks([tarih[0], tarih[-1]])
    kaydetme_yolu = "static/images/grafik2.png"
    # Grafiği images olarak kaydetme...
    fig.savefig(kaydetme_yolu)

#Haftalık Log Zaman Grafiği.
def cizgiGrafik3():
    # Matplotlib grafiği oluşturun
    tarih_ilk_yedi = list(reversed(tarih[:7]))
    fig = Figure(figsize=(6, 4), dpi=100)
    grafik = fig.add_subplot(111)
    grafik.plot(list(reversed(tarih[:7])), list(reversed(adet[:7])), label='_nolegend_',color='green')  # Çizgi grafiğinin rengini değiştirme...
    grafik.set_xlabel("Tarih")  # set_xlabel kullanılmalı
    grafik.set_ylabel("SİSTEM LOGLANMA SAYISI")  # set_ylabel kullanılmalı
    grafik.set_title("Sistem Haftalık Log Meşguliyet Grafiği")  # set_title kullanılmalı
    grafik.set_xticks(range(len(tarih_ilk_yedi)))
    grafik.set_xticklabels(tarih_ilk_yedi,rotation=15)
    kaydetme_yolu = "static/images/grafik3.png"
    # Grafiği images olarak kaydetme...
    fig.savefig(kaydetme_yolu)

#Logların Oranını Veren Pasta Grafiği
def pastagrafik():
    # Pasta grafiğini oluştur
    fig = Figure(figsize=(6, 4), dpi=100)
    grafik = fig.subplots()
    grafik.pie(adet4, labels=uyariAdi, autopct='%1.1f%%', startangle=180)
    grafik.axis('equal')
    kaydetme_yolu = "static/images/grafik4.png"
    # Grafiği images olarak kaydetme...
    fig.savefig(kaydetme_yolu)

powerShellFonksiyon()
tarihAyristirma()
logAyristirma()

#Ayrıştırılmış tarihleri okuyarak listeme ekliyorum ve cizgigrafik fonksiyonuma yolluyorum...
with open("TarihAyristirlmis.txt", "r", encoding="utf-16") as dosya:
    for satir in dosya:
        satir = satir.strip().split()  # Satırı boşluklara göre bölelim
        tarih.append(satir[0])  # İlk kelime tarih
        adet.append(int(satir[1]))  # İkinci kelime adet sayısı

#Ayrıştırılmış Kritikleri okuyarak listeme ekliyorum ve cizgigrafik2 fonksiyonuma yolluyorum...
with open("KritikAyristirlmis.txt", "r", encoding="utf-16") as dosya2:
    for veri in tarih:
        dosya2.seek(0)  # Dosyanın başına dön
        tarih_bulundu = False
        for satir in dosya2:
            satir = satir.strip().split()  # Satırı boşluklara göre bölelim
            if veri == satir[0]:
                tarih2.append(satir[0])  # İlk kelime tarih
                adet3.append(int(satir[2]) * 200)  # üçüncü kelime adet sayısı
                tarih_bulundu = True
                break  # Eşleşen tarihi bulduk, döngüden çık
        if not tarih_bulundu:
            tarih2.append(veri)
            adet3.append(0)

#Ayrıştırılmış uyarı türlerini pastagrafik fonksiyonuma gönderiyorum...
with open("ToplamUyariAdetleri.txt", "r", encoding="utf-16") as dosya3:
    for indeks, satir in enumerate(dosya3):
        if indeks==0:
            continue
        else:
            satir = satir.strip().split()  # Satırı boşluklara göre bölelim
            uyariAdi.append(satir[0])  # İlk kelime
            adet4.append(int(satir[1]))  # İkinci kelime adet sayısı

cizgiGrafik()
cizgiGrafik2()
cizgiGrafik3()
pastagrafik()

#Ayrıştırılmış uyari tiplerini listeme ekliyorum ve flask ile tablo oluşturması için web siteme yönlendiriyorum...
with open("UyariAyristirlmis.txt", "r", encoding="utf-16") as dosya2:
    for indeks, satir in enumerate(dosya2):
        if indeks==0:
            continue
        else:
            satir = satir.strip().split()  # Satırı boşluklara göre bölelim
            uyari.append(satir[0]+" "+satir[1])
            adet2.append(int(satir[2]))  # İkinci kelime adet sayısı

bugununLogSayisi=str(adet[0])
dununLogSayisi=str(adet[1])
ortalamahesaplama=veriSayac/gunsayisi
print(f"Ortlama Günlük Log sayisi {ortalamahesaplama}")


#FLASK KISMI
app = Flask(__name__)
#Verileri hangi çerezde tutulucağını belirttim.
app.secret_key='keycode11'

#Login panel için kullanici bilgileri
users = {
    'bilecik': '123456789',
    'muhendislik': '20092009'
}

@app.route('/')
def mainpage():

    ip = request.remote_addr
    ziyaretciler.append(ip)
    return render_template('login.html',ziyaretciler=ziyaretciler)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error_message='Geçersiz kullanıcı adı veya şifre',ziyaretciler=ziyaretciler)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    if not session.get('logged_in'):
        return render_template('ErrorPage.html')
    return render_template('anasayfa.html',veriSayac=veriSayac,uyari=uyari,adet2=adet2,
                           bugununLogSayisi=bugununLogSayisi,dununLogSayisi=dununLogSayisi,gunsayisi=gunsayisi)

if __name__ == '__main__':
    app.run(debug=True)
