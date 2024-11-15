#!/usr/bin/env python3

from os.path import basename, splitext, exists
import tkinter as tk
from tkinter import messagebox
import requests
import datetime

from tkinter import ttk


class MyEntry(tk.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        if "textvariable" not in kw:
            self.variable = tk.StringVar()
            self.config(textvariable=self.variable)
        else:
            self.variable = kw["textvariable"]

    @property
    def value(self):
        return self.variable.get()

    @value.setter
    def value(self, new: str):
        self.variable.set(new)


class About(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, class_=parent.name)
        self.config()

        btn = tk.Button(self, text="Konec", command=self.close)
        btn.pack()

    def close(self):
        self.destroy()


class Application(tk.Tk):
    name = basename(splitext(basename(__file__.capitalize()))[0])
    name = "Foo"

    def __init__(self):
        super().__init__(className=self.name)
        self.title(self.name)
        self.bind("<Escape>", self.destroy)
        self.lbl = tk.Label(self, text="Směnárna")
        self.lbl.pack()

        self.varAuto = tk.BooleanVar()
        self.chboxAuto = tk.Checkbutton(
            self, text="Automaticky stahovat kurzy", variable=self.varAuto, command=self.chboxAutoClick
        )
        self.chboxAuto.pack()
        self.btnDowland = tk.Button(self, text="Stáhnout", command=self.download)
        self.btnDowland.pack()


        self.lblTransaction= tk.LabelFrame(self, text="Transakce")
        self.lblTransaction.pack(anchor="w", padx=5)
        self.varTransaction.trace_add("read", self.transactionClick)

        self.varTransaction = tk.StringVar(
            value="purchase"
        )



        self.rbtnPurchase = tk.Radiobutton(
            self.lblTransaction, 
            text="Nákup", 
            variable=self.varTransaction, 
            value="purchase"
            )
        self.rbtnSale = tk.Radiobutton(
            self.lblTransaction, 
            text="Prodej", 
            variable=self.varTransaction, 
            value="sale"
            )
        self.rbtnPurchase.pack()
        self.rbtnSale.pack()

        self.chboxCountry = ttk.Combobox(self, values=[])
        self.chboxCountry.set("Vyber zemi:")
        self.chboxCountry.pack(anchor="w", padx=5, pady=5)
        self.chboxCountry.bind("<<ComboboxSelected>>", self.on_select)


        self.lblCourse = tk.LabelFrame(self, text="Kurz")
        self.lblCourse.pack(anchor="w", padx=5, pady=5)
        self.entryAmount = MyEntry(self.lblCourse, state="readonly")
        self.entryAmount.pack()
        self.entryRate = MyEntry(self.lblCourse, state="readonly")
        self.entryRate.pack()


        self.btn = tk.Button(
            self, 
            text="Konec", 
            command=self.destroy
            )
        self.btn.pack()

    
    def transactionClick(self, *arg):
        self.on_select()


    def chboxAutoClick(self):
        if self.varAuto.get():
            self.btnDowland.config(state=tk.DISABLED)
        else:
            self.btnDowland.config(state=tk.NORMAL)
    
    def download(self):
        # kurzy z ČNB
        URL = "https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt"
        try:
            response = requests.get(URL)
            data = response.text
            with open("kurzovni_listek.txt", "w")as f:
                f.write(data)

        except requests.exceptions.ConnectionError as e:
            print(f"Error:? {e}")
            if not exists("kurzovni_listek.txt"):
                messagebox.showerror("Chyba", "Kurzovní lístek nenalezen.")
                return
            
            with open("kurzovni_listek.txt", "r")as f:
                data = f.read()
        
        self.ticket = {}
        for line in data.splitlines()[2:]:
            country,currency,amount,code,rate = line.split("|")
            self.ticket[country] = {
                "currency":currency,
                "amount":amount,
                "code":code,
                "rate":rate
            }
        
        self.chboxCountry.config(values=list(self.ticket.keys()))

    def on_select(self, event=None):
        country = self.chboxCountry.get()
        self.lblCourse.config(text=self.ticket[country]['code'])
        self.amount = int(self.ticket[country]['amount'])
        if self.varTransaction.get() == "purchase":
            self.rate = float(self.ticket[country]['rate'])*0.96
        else:
            self.rate = float(self.ticket[country]['rate'])*1.04

        self.entryAmount.value=self.ticket[country]['amount']
        self.entryRate.value=str(self.rate)

    def destroy(self, event=None):
        super().destroy()


app = Application()
app.mainloop()
