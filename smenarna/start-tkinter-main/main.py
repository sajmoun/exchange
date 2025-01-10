#!/usr/bin/env python3

from os.path import basename, splitext, exists
import tkinter as tk
from tkinter import messagebox
import requests

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

class Application(tk.Tk):
    name = "Směnárna"

    def __init__(self):
        super().__init__(className=self.name)
        self.title(self.name)

        self.lbl = tk.Label(self, text="Směnárna")
        self.lbl.pack()

        self.varAuto = tk.BooleanVar()
        self.chboxAuto = tk.Checkbutton(
            self, text="Automaticky stahovat kurzy", variable=self.varAuto, command=self.chboxAutoClick
        )
        self.chboxAuto.pack()

        self.btnDownload = tk.Button(self, text="Stáhnout", command=self.download)
        self.btnDownload.pack()

        self.lblTransaction = tk.LabelFrame(self, text="Transakce")
        self.lblTransaction.pack(anchor="w", padx=5)

        self.varTransaction = tk.StringVar(value="purchase")
        self.varTransaction.trace_add("write", self.update_rate)

        self.rbtnPurchase = tk.Radiobutton(
            self.lblTransaction, text="Nákup", variable=self.varTransaction, value="purchase"
        )
        self.rbtnSale = tk.Radiobutton(
            self.lblTransaction, text="Prodej", variable=self.varTransaction, value="sale"
        )
        self.rbtnPurchase.pack()
        self.rbtnSale.pack()

        self.chboxCountry = ttk.Combobox(self, values=[])
        self.chboxCountry.set("Vyber zemi:")
        self.chboxCountry.pack(anchor="w", padx=5, pady=5)
        self.chboxCountry.bind("<<ComboboxSelected>>", self.update_rate)

        self.lblCourse = tk.LabelFrame(self, text="Kurz")
        self.lblCourse.pack(anchor="w", padx=5, pady=5)

        self.entryAmount = MyEntry(self.lblCourse, state="readonly")
        self.entryAmount.pack()

        self.entryRate = MyEntry(self.lblCourse, state="readonly")
        self.entryRate.pack()

        self.lblInput = tk.LabelFrame(self, text="Částka")
        self.lblInput.pack(anchor="w", padx=5, pady=5)

        self.entryInput = MyEntry(self.lblInput)
        self.entryInput.pack()
        self.entryInput.variable.trace_add("write", self.update_result)

        self.lblResult = tk.LabelFrame(self, text="Výsledek")
        self.lblResult.pack(anchor="w", padx=5, pady=5)

        self.entryResult = MyEntry(self.lblResult, state="readonly")
        self.entryResult.pack()

        self.btn = tk.Button(self, text="Konec", command=self.destroy)
        self.btn.pack()

        self.ticket = {}
        self.amount = 1
        self.rate = 1.0

    def chboxAutoClick(self):
        if self.varAuto.get():
            self.btnDownload.config(state=tk.DISABLED)
            self.download()
        else:
            self.btnDownload.config(state=tk.NORMAL)

    def download(self):
        URL = "https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt"
        try:
            response = requests.get(URL)
            data = response.text
            with open("kurzovni_listek.txt", "w") as f:
                f.write(data)
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {e}")
            if not exists("kurzovni_listek.txt"):
                messagebox.showerror("Chyba", "Kurzovní lístek nenalezen.")
                return

            with open("kurzovni_listek.txt", "r") as f:
                data = f.read()

        self.ticket = {}
        for line in data.splitlines()[2:]:
            country, currency, amount, code, rate = line.split("|")
            self.ticket[country] = {
                "currency": currency,
                "amount": int(amount),
                "code": code,
                "rate": float(rate)
            }

        self.chboxCountry.config(values=list(self.ticket.keys()))

    def update_rate(self, event=None, *args):
        country = self.chboxCountry.get()
        if country not in self.ticket:
            return

        self.lblCourse.config(text=self.ticket[country]['code'])
        self.amount = self.ticket[country]['amount']

        if self.varTransaction.get() == "purchase":
            self.rate = self.ticket[country]['rate'] * 0.96
        else:
            self.rate = self.ticket[country]['rate'] * 1.04

        self.entryAmount.value = str(self.amount)
        self.entryRate.value = f"{self.rate:.2f}"
        self.update_result()

    def update_result(self, *args):
        try:
            input_amount = float(self.entryInput.value)
            result = input_amount * self.rate / self.amount
            self.entryResult.value = f"{result:.2f}"
        except ValueError:
            self.entryResult.value = ""

    def destroy(self, event=None):
        super().destroy()

app = Application()
app.mainloop()
