# Preparação do ambiente ----
## Instalação e importação de bibliotecas ====
# install.packages("rstudioapi")
# install.packages("data.table")
# install.packages("ggplot2")
# install.packages("readxl")
# install.packages("dplyr")
# install.packages("stringi")
# install.packages("shadowtext")
library("rstudioapi")
library("data.table")
library("ggplot2")
library("readxl")
library("dplyr")
library("stringi")

## Fazendo o diretório de trabalho o mesmo onde o arquivo .r está ====
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

## Lendo o arquivo csv e o convertendo em data.table ====
dt <- read.csv(file = "vacinabh.csv")
setDT(dt)

## Visualizando os dados e os deixando mais legíveis ====
View(dt)
colnames(dt) <- c("id", "idade", "sexo_bio", "raca_cor",
                  "municipio", "uf", "vac_codigo", "categoria",
                  "vac_fabricante", "vac_aplicacao", "vac_dose"
                  )
dt$vac_codigo <- NULL

# Análise Monovariada ----

## Análise sobre a idade ====
### Separando por faixas etárias ####
idade_data <- as.data.table(table(dt$idade))
colnames(idade_data) <- c("idade", "quantia")
idade_data$idade <- as.numeric(idade_data$idade)
summary(dt$idade)
idade_data$faixa <- cut(idade_data$idade,
                            c(2, 20, 30, 40, 50, 60, 70, 80, 122)
                            )
idade_data$idade <- NULL
idade_data <- idade_data[, sum(quantia), by=faixa]
colnames(idade_data) <- c("faixa", "vacinas")

### Criando o gráfico ####
ggplot(idade_data, aes(x = faixa, y = vacinas)) +
  geom_bar(
    stat = "identity",
    fill = "darkgreen",
  ) +
  labs(title = "Vacinas por faixa etária",
       x = "Faixa etária",
       y = "Vacinas"
  ) +
  theme_linedraw()+
  scale_x_discrete(
    labels = c(
      "< 20",
      "de 20\na 30",
      "de 30\na 40",
      "de 40\na 50",
      "de 50\na 60",
      "de 60\na 70",
      "de 70\na 80",
      "> 80"
      )
  ) +
  scale_y_continuous(
    breaks = seq(0, 2400, 400)
  ) +
  geom_text(
    aes(
      label = paste(
        vacinas,
        "\n(",
        as.character(
          round(vacinas/sum(vacinas)*100, digits = 1)),
        "%)",
        sep = ""
        )
      ), 
    vjust = 1.2 * fifelse(idade_data$vacinas > 500, 1, -0.2),
    color = fifelse(idade_data$vacinas > 500, "white", "black")
  )

ggsave("idade_plot.png", width = 7, height = 5, bg="white")

## Análise sobre o sexo biológico ====
biosex_data <- as.data.table(prop.table(table(dt$sexo_bio)) * 100)
colnames(biosex_data) <- c("sexo_bio", "porcentagem")

ggplot(biosex_data, aes(x="", y = porcentagem, fill = sexo_bio)) +
  geom_bar(width = 1, stat = "identity", color = "white") +
  coord_polar("y", start = 0) +
  theme_void() +
  scale_fill_brewer(palette = "Dark2") +
  labs(title = "Porcentagem de vacinados por sexo biológico",
       fill = "Sexo biológico"
       ) +
  geom_text(aes(x="",
                 label = paste(as.character(round(porcentagem, digits = 2)), "%")
                 ),
            position = position_stack(vjust = 0.5)
            )
            
ggsave("sexbio_plot.png", width = 5, height = 5, bg="white")


## Análise sobre raça/cor ====
raca_cor_data <- as.data.table(prop.table(table(dt$raca_cor)) * 100)
colnames(raca_cor_data) <- c("raca_cor", "quantia")

ggplot(raca_cor_data, aes(x="", y = quantia, fill = raca_cor)) +
  geom_bar(width = 1, stat = "identity", color = "white") +
  coord_polar("y", start = 0) +
  theme_void() +
  scale_fill_brewer(palette = "Dark2") +
  labs(title = "Porcentagem de vacinados por raça/cor", fill = "Raça/Cor") +
  geom_text(aes(x = 1.8,
                label = paste(as.character(round(quantia, digits = 2)),"%")
                ),
            position = position_stack(vjust = 0.5)
            )

ggsave("raca_cor_plot.png", width = 5, height = 5, bg="white")

## Análise sobre o município ====
# O passo abaixo é para garantir que estamos tratando de uma
# cidade específica e não de duas cidades de nomes iguais,
# mas em estados diferentes.
cidade_estado <- with(dt, paste(municipio, uf))
muni_data <- as.data.table(table(cidade_estado))
muni_data <- muni_data[-1,]
colnames(muni_data) <- c("municipio", "vacinados")
muni_data <- filter(muni_data, municipio != "")

### Sobre as cidades ####
url <- "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/POP2021_20221109.xls"
download.file(url, paste(getwd(), "/cidades.xls", sep=""))
cidades_dt <- as.data.table(read_excel("cidades.xls", sheet = 2))
names(cidades_dt) <- c("uf", "cod. uf", "cod. mun", "municipio", "pop")
cidades_dt$`cod. mun` <- NULL
cidades_dt$`cod. uf` <- NULL
cidades_dt <- cidades_dt[-1,]
cidades_dt$municipio <- lapply(cidades_dt$municipio, toupper)
cidades_dt$municipio <- lapply(cidades_dt$municipio,
                               function(x)  stri_trans_general(x, id = "Latin-ASCII")
                               )
cidades_dt$municipio <- with(cidades_dt, paste(municipio, uf))
cidades_dt$uf <- NULL
cidades_dt <- filter(cidades_dt, municipio %in% muni_data$municipio)

### Vacinados nos municípios ####
# Tirando dados inválidos como "Não informado XX"
muni_data <- muni_data[muni_data$municipio %in% cidades_dt$municipio]
cidades_dt <- cidades_dt[order(municipio)]
muni_data <- muni_data[order(municipio)]
muni_data$pop <- cidades_dt$pop[match(cidades_dt$municipio, muni_data$municipio)]
muni_data$porcentagem <- with(muni_data, round(vacinados/as.numeric(pop)*100, 2))

### Gráficos sobre município de origem dos vacinados
regiao_metropolitana <- c(
  "BELO HORIZONTE MG",
  "CONTAGEM MG",
  "BETIM MG",
  "RIBEIRAO DAS NEVES MG",
  "SETE LAGOAS MG",
  "SANTA LUZIA MG",
  "IBIRITE MG",
  "SABARA MG",
  "VESPASIANO MG",
  "NOVA LIMA MG",
  "BALDIM MG",
  "BRUMADINHO MG",
  "CAETE MG",
  "CAPIM BRANCO MG",
  "CONFINS MG",
  "ESMERALDAS MG",
  "FLORESTAL MG",
  "IGARAPE MG",
  "ITAGUARA MG",
  "ITATIAIUCU MG",
  "JABOTICATUBAS MG",
  "JUATUBA MG",
  "LAGOA SANTA MG", 
  "MARIA CAMPOS MG",
  "MATEUS LEME MG",
  "MATOZINHOS MG",
  "NOVA UNIAO MG",
  "PEDRO LEOPOLDO MG",
  "RAPOSOS MG",
  "RIO ACIMA MG",
  "RIO MANSO MG",
  "SAO JOAQUIM DE BICAS MG",
  "SAO JOSE DA LAPA MG",
  "SARZEDO MG",
  "TAQUARACU DE MINAS MG"
  )

grande_bh <- c(
  "BELO HORIZONTE MG",
  "CONTAGEM MG",
  "BETIM MG",
  "RIBEIRAO DAS NEVES MG",
  "SETE LAGOAS MG",
  "SANTA LUZIA MG",
  "IBIRITE MG",
  "SABARA MG",
  "VESPASIANO MG",
  "NOVA LIMA MG"
)

muni_data$regiao_metrop <- muni_data[, fifelse(municipio %in% regiao_metropolitana, vacinados, 0)]

muni_data[, sum(regiao_metrop)]

ggplot(
  muni_data,
  aes(
    x = c(
      muni_data[municipio == "BELO HORIZONTE MG", vacinados/sum(muni_data$vacinados)*100],
      muni_data[municipio %in% grande_bh, sum(vacinados/sum(muni_data$vacinados))*100],
      muni_data[municipio %in% regiao_metropolitana, sum(vacinados/sum(muni_data$vacinados))*100],
      100 - muni_data[municipio %in% regiao_metropolitana, sum(vacinados/sum(muni_data$vacinados))*100]
    ),
    y = c("Belo Horizonte", "Grande BH", "Região Metropolitana", "Outros")
  )
) +
  geom_col()
### Gráficos sobre os municípios ####
ggplot(tail(muni_data[order(porcentagem)]),
       aes(x=reorder(municipio, -porcentagem), y=porcentagem, fill = municipio))+ 
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette = "Dark2") +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(title="Municípios com maior porcentagem de vacinados",
       x = "",
       y = ""
  ) +
  coord_flip()

ggsave("porcentagem_por_municipio_plot.png", width = 8, height = 5)

ggplot(tail(muni_data[order(vacinados)]),
       aes(x=reorder(municipio, -vacinados), y=vacinados, fill = municipio))+ 
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette = "Dark2") +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(title="Municípios com maior número de vacinas aplicadas",
       x = "",
       y = ""
  ) +
  coord_flip()

ggsave("quantidade_de_vacinados_por_municipio_plot.png", width = 7, height = 5)

## Análise sobre a categoria ====
categoria_data <- as.data.table(table(dt$categoria))
colnames(categoria_data) <- c("categoria", "vacinados")
categoria_data <- categoria_data[categoria != ""]
categoria_data <- categoria_data[order(vacinados)]
categoria_data[11,2] <- sum(categoria_data$vacinados[1:9]) +
  categoria_data[11,2]
categoria_data <- categoria_data[-(1:9)]
categoria_data$porcentagem <- categoria_data[, round(vacinados/sum(vacinados)*100, digits = 2)]

ggplot(
  categoria_data,
  aes(
    x="",
    y = porcentagem,
    fill = categoria_data[, paste(categoria, " (", porcentagem, "%)", sep = "")]
  )
) +
  geom_bar(
    width = 1,
    stat = "identity",
    color = "black"
  ) +
  coord_polar("y", start = 0) +
  theme_void() +
  scale_fill_brewer(palette = "Dark2") +
  labs(title = "Vacinados por categoria de vacinação", fill = "Categoria")


ggsave("categoria_plot.png", width = 5, height = 5, bg = "white")

## Análise sobre a fabricante da vacina ====
fabricante_data <- as.data.table(table(dt$vac_fabricante))
colnames(fabricante_data) <- c("fabricante", "vacinas")
fabricante_data[7,2] <- fabricante_data[6,2] + fabricante_data[7,2]
fabricante_data <- fabricante_data[-6]

ggplot(fabricante_data, aes(x=reorder(fabricante, vacinas), y=vacinas, fill=fabricante)) +
  geom_col(width=0.6, color = "black") +
  coord_flip() +
  theme(legend.position = "none") +
  theme_linedraw() +
  theme(legend.position = "none") +
  geom_text(aes(label = paste(as.character(
      round(vacinas/sum(vacinas)*100, digits = 2)),"%"
    )),
    hjust = 1.1 * fifelse(fabricante_data$vacinas > 1000, 1, -0.1)
  ) +
  scale_fill_brewer(palette = "Set1") +
  labs(
    title = "Porcentagem e quantidade de vacinas por fabricante",
    x = "",
    y = "Vacinas"
  )

ggsave("fabricantes_plot.png", width = 8, height = 5, bg = "white")

## Análise temporal ====
aplicacao_data <- as.data.table(table(dt$vac_aplicacao))
colnames(aplicacao_data) <- c("data", "vacinas")
aplicacao_data <- aplicacao_data[order(data)]
aplicacao_data$acumulado <- cumsum(aplicacao_data$vacinas)
aplicacao_data$data <-  as.Date(aplicacao_data$data)

ggplot(aplicacao_data, aes(x=data, y=acumulado)) +
  geom_line(color = "steelblue", linewidth = 1.5) +
  scale_x_date(
    date_labels = "%b\n%Y",
    date_breaks = "3 month",
    date_minor_breaks = "1 month"
  ) +
  scale_y_continuous(
    breaks = seq(0, 13000, 2500)
  ) +
  theme_linedraw() +
  labs(
    title = "Vacinas ao longo do tempo",
    x = "Data",
    y = "Total de vacinas aplicadas"
  ) + 
  theme(axis.text.x = element_text(hjust = 1))

ggsave("aplicacao_plot.png", width = 6, height = 3)

# Análise Multivariada ----
## Análise sobre a idade e o sexo ====
idade_sexo_data <- select(dt, idade, sexo_bio)
idade_sexo_data$faixa <- cut(
  idade_sexo_data$idade,
  c(2, 20, 30, 40, 50, 60, 70, 80, 122)
  )
idade_sexo_data$idade <- NULL
idade_sexo_data$faixa <- as.character(idade_sexo_data$faixa)
idade_sexo_data$faixa <- idade_sexo_data[, paste(faixa, sexo_bio)]
idade_sexo_data$sexo_bio <- NULL
idade_sexo_data <- as.data.table(table(idade_sexo_data$faixa))
colnames(idade_sexo_data) <- c("faixa", "vacinas")
idade_sexo_data$sexo_bio <- with(
  idade_sexo_data,
  substr(faixa, nchar(faixa), nchar(faixa))
)
idade_sexo_data$faixa <- with(
  idade_sexo_data,
  substr(faixa, 1, nchar(faixa)-2)
)

ggplot(
  idade_sexo_data,
  aes(
    x = faixa,
    y = vacinas,
    fill = sexo_bio
  )
) + geom_bar(stat = "identity", position = "dodge", color = "black") +
  theme_linedraw() +
  scale_x_discrete(
    labels = c(
      "< 20",
      "de 20\na 30",
      "de 30\na 40",
      "de 40\na 50",
      "de 50\na 60",
      "de 60\na 70",
      "de 70\na 80",
      "> 80"
    )
  ) +
  scale_y_continuous(
    breaks = seq(0, 1200, 200)
  ) +
  labs(
    title = "Vacinas por faixa etária e sexo biológico",
    x = "Faixa etária",
    y = "Vacinas",
    fill = "Sexo\nBiológico"
  )

ggsave("idade_sexo_plot.png", width = 7, height = 4, bg = "white")
  
## Análise por sexo biológico e raça/cor ====
sexo_cor_data <- as.data.table(table(select(dt, sexo_bio, raca_cor)))
setkey(sexo_cor_data, raca_cor)
sexo_cor_data$total <- sexo_cor_data[, sum(N), by=raca_cor][J(sexo_cor_data$raca_cor), 2]

ggplot(
  sexo_cor_data,
  aes(
    x = raca_cor,
    y = N,
    fill = sexo_bio
  )
) + 
  geom_col(position = "stack", color = "black") +
  theme_linedraw() +
  scale_x_discrete(
    labels = c(
      "Amarela",
      "Branca",
      "Indígena",
      "Parda",
      "Preta",
      "Sem\ninformação"
    )
  ) +
  labs(
    title = "Vacinas por raça/cor e sexo biológico",
    subtitle = "Porcentagem dentro da própria categoria de raça/cor",
    y = "Vacinas",
    x = "Raça/cor",
    fill = "Sexo\nBiológico"
  ) +
  geom_text(
    aes(
      label = paste(
        as.character(
          round(N/total*100, digits = 1)),
        "%",
        sep = ""
      )
    ), 
    vjust = c(-0.5, 1.5, 2.5, 1.5, -3, -1, 2, 1.5, -0.25, 1.5, 1.75, 1.5),
    color = fifelse(sexo_cor_data$N > 100, "white", "black")
  )

ggsave("sexo_cor_plot.png", width = 6, height = 4)

## Análise sobre sexo biológico na série temporal ====
sexo_aplicacao_data <- select(dt, sexo_bio, vac_aplicacao)
colnames(sexo_aplicacao_data) <- c("sexo_bio", "aplicacao")
f_aplicacao_data <- as.data.table(table(sexo_aplicacao_data[sexo_bio == "F"]$aplicacao))
m_aplicacao_data <- as.data.table(table(sexo_aplicacao_data[sexo_bio == "M"]$aplicacao))
f_aplicacao_data$acumulado <- cumsum(f_aplicacao_data$N)
m_aplicacao_data$acumulado <- cumsum(m_aplicacao_data$N)
colnames(f_aplicacao_data) <- c("aplicacao", "N", "acumulado")
colnames(m_aplicacao_data) <- c("aplicacao", "N", "acumulado")
f_aplicacao_data$aplicacao <- as.Date(f_aplicacao_data$aplicacao)
m_aplicacao_data$aplicacao <- as.Date(m_aplicacao_data$aplicacao)

ggplot() +
  geom_line(
    data = f_aplicacao_data,
    aes(
      x = aplicacao,
      y = acumulado
    ),
    color = "steelblue",
    linewidth = 1.5
  ) +
  geom_line(
    data = m_aplicacao_data,
    aes(
      x = aplicacao,
      y = acumulado
    ),
    color = "orange",
    linewidth = 1.5
  ) +
  scale_x_date(
    date_labels = "%b\n%Y",
    date_breaks = "3 month",
    date_minor_breaks = "1 month"
  ) +
  scale_y_continuous(
    breaks = seq(0, 7000, 1000)
  ) +
  theme_linedraw() +
  theme(
    axis.text.x = element_text(hjust = 1),
  ) +
  labs(
    title = "Vacinas por sexo biológico ao longo do tempo",
    subtitle = "Femenino (azul) e Masculino (laranja)",
    x = "Data",
    y = "Vacinas"
  )

ggsave("sexo_aplicacao_plot.png", width = 5, height = 3)

## Análise temporal dos fabricante doses ====
fabricante_aplicacao_data <- select(dt, vac_fabricante, vac_aplicacao)
colnames(fabricante_aplicacao_data) <- c("fabricante", "aplicacao")

aplicacao_por_fabricante <- select(dt, vac_aplicacao)
setkey(aplicacao_por_fabricante, vac_aplicacao)
for (data in aplicacao_por_fabricante$vac_aplicacao) {
  for (fabricante in levels(dt$vac_fabricante)) {
    
  }
}
  as.data.table(table(fabricante_aplicacao_data[fabricante == "PFIZER"]$aplicacao))


ggplot(
  fabricante_aplicacao_data,
  aes(
    x = 
  )
)