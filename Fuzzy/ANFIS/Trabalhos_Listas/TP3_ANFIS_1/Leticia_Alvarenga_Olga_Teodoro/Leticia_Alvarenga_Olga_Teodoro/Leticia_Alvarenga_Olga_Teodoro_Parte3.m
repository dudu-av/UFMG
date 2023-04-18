%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% Universidade Federal de Minas Gerais - UFMG
%% Engenharia de Sistemas - 2021/1
%% Letícia Alvarenga Machado - 2017111427
%% Olga Camila Teodoro de Rezende Lara - 2018104106
%% 
%% Previsão de uma série temporal
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


clear all;
close all;
clc

%carregamento basico
t = [19:1:995];
t = t'
load mg.mat

%entradas do modelo
ys = x(t + 6);
x1 = x(t - 18);
x2 = x(t - 12);
x3 = x(t - 6);
x4 = x(t);

%configuracao das iterações e teste
geracoes = 200;
tam=size(t,1);
tam_trein=0.8*tam;
tam_verif=0.2*tam;
inicio_teste=tam_trein+1;

%treinamento anfis
input = genfis1([x1(1:tam_trein), x2(1:tam_trein), x3(1:tam_trein), x4(1:tam_trein), ys(1:tam_trein)], 2, 'gbellmf', 'linear');
output = anfis([x1(1:tam_trein), x2(1:tam_trein), x3(1:tam_trein), x4(1:tam_trein) ,ys(1:tam_trein)], input, geracoes);

%criação dos parametros p avaliação
yc_verif = evalfis ([x1(inicio_teste:tam), x2(inicio_teste:tam), x3(inicio_teste:tam), x4(inicio_teste:tam)],output);
yd_verif = ys(inicio_teste:tam);

%comparação do teste feito
figure(1)
plot(1:tam_verif,yd_verif, 'b')
hold on
plot(1:tam_verif,yc_verif,'r')
title('Testes','FontSize',10);
legend('Valores Reais','Valores Previstos');
erro_verif = 1/2*sumsqr(yc_verif - yd_verif);
fprintf('teste %d', erro_verif);

%também é necessário comparar os dados do teste
%criacão dos parametros para avaliação
yc_trein = evalfis([x1(1:tam_trein), x2(1:tam_trein), x3(1:tam_trein), x4(1:tam_trein)], output);
yd_trein = ys(1:tam_trein);

figure(2)
plot(1:tam_trein,yd_trein, 'b')
hold on
plot(1:tam_trein,yc_trein,'r')
title('Treinamento','FontSize',10);
legend('Valores reais','Valores previstos');
erro_trein = 1/2*sumsqr(yc_trein - yd_trein);
fprintf('treinamento %d', erro_trein);
