import tabula

tables = tabula.read_pdf("Stundenplan.pdf", pages=33)
print(tables[0])
